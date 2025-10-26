"""
Модуль для парсинга расписания учебных групп.
Улучшенная версия с обработкой подгрупп, множественных преподавателей и всех edge cases.
"""

import asyncio
from datetime import date, datetime, timedelta
from time import perf_counter
from typing import Optional
from html.parser import HTMLParser

import aiohttp
import structlog

from .models import Lesson, ParseResult, WeekType, ChangeType
from .db import get_database, Database
from .utils import (
    DAY_MAPPING,
    LESSON_TIMES,
    parse_lesson_info,
    get_monday_of_week,
    get_week_type_for_date,
    retry_async,
    normalize_text
)
from .config import get_config

logger = structlog.get_logger()


class ScheduleHTMLParser(HTMLParser):
    """Парсер HTML-таблицы расписания."""

    def __init__(self):
        """Инициализация парсера."""
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.current_row_flags: list[dict[str, bool]] = []
        self.rows = []
        self.row_metadata: list[dict[str, bool]] = []
        self.cell_data = []
        self.cell_has_blue = False
        self.group_name: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """Обработка открывающего тега."""
        match tag.lower():
            case "table":
                self.in_table = True
            case "tr" if self.in_table:
                self.in_row = True
                self.current_row = []
                self.current_row_flags = []
            case "td" if self.in_row:
                self.in_cell = True
                self.cell_data = []
                self.cell_has_blue = False
            case "font":
                # Извлекаем название группы из цветного шрифта
                for attr, value in attrs:
                    if attr == "color":
                        color = value.lower()
                        if color == "#ff00ff":
                            self.in_cell = True
                        if color == "#0000ff" and self.in_cell:
                            self.cell_has_blue = True

    def handle_endtag(self, tag: str) -> None:
        """Обработка закрывающего тега."""
        match tag.lower():
            case "table":
                self.in_table = False
            case "tr" if self.in_row:
                self.in_row = False
                if self.current_row:
                    row_flag = {
                        "has_blue": any(flag.get("has_blue", False) for flag in self.current_row_flags)
                    }
                    self.rows.append(self.current_row)
                    self.row_metadata.append(row_flag)
            case "td" | "font" if self.in_cell:
                self.in_cell = False
                cell_text = ''.join(self.cell_data).strip()
                self.current_row.append(cell_text)
                self.current_row_flags.append({"has_blue": self.cell_has_blue})
                self.cell_data = []
                self.cell_has_blue = False

    def handle_data(self, data: str) -> None:
        """Обработка текстовых данных."""
        if self.in_cell:
            self.cell_data.append(data)
        elif not self.group_name and "учебной группы:" in data:
            # Следующий текст после этой фразы - название группы
            pass

    def get_schedule_data(self) -> list[tuple[list[str], dict[str, bool]]]:
        """
        Получить распарсенные данные расписания.

        Returns:
            Список строк таблицы, каждая строка - список ячеек с метаданными
        """
        # Пропускаем первые 2 строки (заголовки "Пары" и "Время")
        if len(self.rows) <= 2:
            return []
        return [
            (row, self.row_metadata[idx])
            for idx, row in enumerate(self.rows[2:], start=2)
        ]


async def fetch_schedule_html(url: str) -> str:
    """
    Загрузить HTML страницы расписания.

    Args:
        url: URL страницы расписания

    Returns:
        HTML содержимое страницы

    Raises:
        aiohttp.ClientError: При ошибках загрузки
    """
    config = get_config()

    async def _fetch() -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url,
                    headers={"User-Agent": config.user_agent},
                    timeout=aiohttp.ClientTimeout(total=config.request_timeout)
            ) as response:
                response.raise_for_status()
                # Кодировка windows-1251 указана в мета-теге
                return await response.text(encoding='windows-1251')

    return await retry_async(_fetch)


def parse_schedule_html(html: str, group_id: int) -> tuple[list[Lesson], list[Lesson]]:
    """
    Парсинг HTML расписания в структурированные данные.

    Поддерживает множественные подгруппы в одной записи.
    """
    parser = ScheduleHTMLParser()
    parser.feed(html)

    schedule_data = parser.get_schedule_data()

    even_lessons = []
    odd_lessons = []

    # Текущая дата для расчета
    today = date.today()

    # Определяем текущий и следующий тип недели с учетом выделения на сайте
    current_week_type = WeekType(get_week_type_for_date(today))
    next_week_type = WeekType.ODD if current_week_type == WeekType.EVEN else WeekType.EVEN

    current_week_monday = get_monday_of_week(today)
    next_week_monday = current_week_monday + timedelta(days=7)

    highlight_present = any(metadata.get("has_blue", False) for _, metadata in schedule_data)

    # Fallback на старую логику, если подсветки нет вообще
    monday_even = get_monday_of_week(today, week_type="even")
    monday_odd = get_monday_of_week(today, week_type="odd")

    # Счётчики для логирования
    total_processed = 0
    skipped_empty = 0
    skipped_invalid = 0
    with_subgroups = 0
    with_multiple_teachers = 0

    # Обрабатываем строки расписания
    for row_idx, (row, metadata) in enumerate(schedule_data):
        if not row or len(row) < 2:
            continue

        # Первая ячейка - день недели
        day_str = normalize_text(row[0]).lower()
        if not day_str:
            continue

        has_highlight = metadata.get("has_blue", False)
        row_cells = row[1:]

        if highlight_present:
            if has_highlight:
                week_type = current_week_type
                base_monday = current_week_monday
            else:
                week_type = next_week_type
                base_monday = next_week_monday
        else:
            week_type = WeekType.ODD if has_highlight else WeekType.EVEN
            base_monday = monday_odd if week_type == WeekType.ODD else monday_even

        # Получаем номер дня недели
        day_of_week = DAY_MAPPING.get(day_str[:3])
        if not day_of_week:
            logger.warning("unknown_day_of_week", day_str=day_str, row_idx=row_idx)
            continue

        # Рассчитываем дату урока
        days_offset = day_of_week - 1
        lesson_date = base_monday + timedelta(days=days_offset)

        # Обрабатываем каждую пару
        for lesson_number, cell_text in enumerate(row_cells, start=1):
            total_processed += 1

            # Пропускаем пустые уроки
            if not cell_text or cell_text.strip() in ('_', ''):
                skipped_empty += 1
                continue

            # Парсим информацию об уроке
            lesson_info = parse_lesson_info(cell_text)

            if not lesson_info.name:
                skipped_invalid += 1
                logger.debug(
                    "lesson_no_name",
                    raw_text=cell_text,
                    day=day_of_week,
                    lesson_number=lesson_number,
                    week_type=week_type.value
                )
                continue

            # Получаем время урока
            start_time, end_time = LESSON_TIMES.get(lesson_number, (None, None))
            if not start_time:
                logger.warning(
                    "invalid_lesson_number",
                    lesson_number=lesson_number,
                    day=day_of_week
                )
                continue

            # Собираем данные о преподавателях и аудиториях
            teacher_name = '; '.join(lesson_info.teachers) if lesson_info.teachers else None
            cabinet_number = '; '.join(lesson_info.cabinets) if lesson_info.cabinets else None

            # Формируем название с учетом подгруппы
            lesson_name = lesson_info.name
            if lesson_info.subgroup:
                lesson_name = f"{lesson_info.name} (подгруппа {lesson_info.subgroup})"

            # Логируем интересные случаи
            if lesson_info.subgroup:
                with_subgroups += 1
            if len(lesson_info.teachers) > 1:
                with_multiple_teachers += 1

            # Создаем объект урока
            lesson = Lesson(
                group_id=group_id,
                name=lesson_info.name,
                lesson_date=lesson_date,
                day_of_week=day_of_week,
                lesson_number=lesson_number,
                start_time=start_time,
                end_time=end_time,
                teacher_name=teacher_name,
                cabinet_number=cabinet_number,
                week_type=week_type,
                lesson_type=lesson_info.lesson_type,  # Добавлено
                raw_text=cell_text,
                subgroup=lesson_info.subgroup
            )

            # Добавляем в соответствующий список
            if week_type == WeekType.EVEN:
                even_lessons.append(lesson)
            else:
                odd_lessons.append(lesson)

    # Логируем статистику парсинга
    logger.info(
        "schedule_parsing_stats",
        group_id=group_id,
        total_cells_processed=total_processed,
        skipped_empty=skipped_empty,
        skipped_invalid=skipped_invalid,
        lessons_with_subgroups=with_subgroups,
        lessons_with_multiple_teachers=with_multiple_teachers,
        even_lessons=len(even_lessons),
        odd_lessons=len(odd_lessons)
    )

    return even_lessons, odd_lessons

async def compare_and_update_lessons(
        db: Database,
        group_id: int,
        new_lessons: list[Lesson],
        week_type: WeekType,
        conn=None
) -> tuple[int, int, int]:
    """
    Сравнить новые уроки с существующими и обновить БД.

    Улучшенная версия с учётом подгрупп при сравнении.

    Args:
        db: Экземпляр базы данных
        group_id: ID группы
        new_lessons: Новые распарсенные уроки
        week_type: Тип недели
        conn: Опциональное существующее соединение

    Returns:
        Кортеж (добавлено, обновлено, удалено)
    """

    logger.info(
        "lessons_compare_started",
        group_id=group_id,
        week_type=week_type.value,
        incoming=len(new_lessons)
    )

    def _shorten(details: list[dict], limit: int = 10) -> dict:
        """Сократить список деталей для логирования."""
        if len(details) <= limit:
            return {"items": details, "remaining": 0}
        return {
            "items": details[:limit],
            "remaining": len(details) - limit
        }

    async def _process(connection) -> tuple[int, int, int]:
        phase_started = perf_counter()
        existing_lessons = await db.get_existing_lessons(group_id, week_type, conn=connection)

        # Создаём маппинг с учётом подгруппы
        existing_map = {
            (l.day_of_week, l.lesson_number, l.subgroup): l
            for l in existing_lessons
        }

        new_map = {
            (l.day_of_week, l.lesson_number, l.subgroup): l
            for l in new_lessons
        }

        to_insert = []
        to_update = []
        to_delete = []

        # Находим новые и изменённые уроки
        for key, new_lesson in new_map.items():
            existing_lesson = existing_map.get(key)
            if existing_lesson is None:
                to_insert.append(new_lesson)
            elif existing_lesson != new_lesson:
                new_lesson.lesson_id = existing_lesson.lesson_id
                to_update.append((existing_lesson, new_lesson))

        # Находим удалённые уроки
        for key, existing_lesson in existing_map.items():
            if key not in new_map:
                to_delete.append(existing_lesson)

        logger.info(
            "lessons_operations_prepared",
            group_id=group_id,
            week_type=week_type.value,
            existing=len(existing_lessons),
            to_insert=len(to_insert),
            to_update=len(to_update),
            to_delete=len(to_delete)
        )

        added = 0
        updated = 0
        deleted = 0

        added_details: list[dict] = []
        updated_details: list[dict] = []
        deleted_details: list[dict] = []

        # Выполняем операции в транзакции
        async with connection.transaction():
            # Вставка новых уроков
            if to_insert:
                logger.info(
                    "lessons_insert_batch_start",
                    group_id=group_id,
                    week_type=week_type.value,
                    count=len(to_insert)
                )
                for new_lesson in to_insert:
                    lesson_id = await db.insert_lesson(new_lesson, conn=connection)
                    await db.log_schedule_change(
                        lesson_id,
                        ChangeType.NEW,
                        new_data={
                            "name": new_lesson.name,
                            "teacher": new_lesson.teacher_name,
                            "subgroup": new_lesson.subgroup,
                            "cabinet": new_lesson.cabinet_number
                        },
                        conn=connection
                    )
                    added += 1
                    added_details.append({
                        "lesson_id": lesson_id,
                        "name": new_lesson.name,
                        "type": new_lesson.lesson_type,
                        "day": new_lesson.day_of_week,
                        "number": new_lesson.lesson_number,
                        "teacher": new_lesson.teacher_name,
                        "subgroup": new_lesson.subgroup
                    })

            # Обновление существующих уроков
            if to_update:
                logger.info(
                    "lessons_update_batch_start",
                    group_id=group_id,
                    week_type=week_type.value,
                    count=len(to_update)
                )
                for existing_lesson, new_lesson in to_update:
                    await db.update_lesson(new_lesson, conn=connection)
                    await db.log_schedule_change(
                        existing_lesson.lesson_id,
                        ChangeType.UPDATE,
                        old_data={
                            "name": existing_lesson.name,
                            "teacher": existing_lesson.teacher_name,
                            "subgroup": existing_lesson.subgroup,
                            "cabinet": existing_lesson.cabinet_number
                        },
                        new_data={
                            "name": new_lesson.name,
                            "teacher": new_lesson.teacher_name,
                            "subgroup": new_lesson.subgroup,
                            "cabinet": new_lesson.cabinet_number
                        },
                        conn=connection
                    )
                    updated += 1
                    updated_details.append({
                        "lesson_id": existing_lesson.lesson_id,
                        "old_name": existing_lesson.name,
                        "new_name": new_lesson.name,
                        "type": new_lesson.lesson_type,
                        "day": new_lesson.day_of_week,
                        "number": new_lesson.lesson_number,
                        "subgroup": new_lesson.subgroup
                    })

            # Удаление отсутствующих уроков
            if to_delete:
                logger.info(
                    "lessons_delete_batch_start",
                    group_id=group_id,
                    week_type=week_type.value,
                    count=len(to_delete)
                )
                for existing_lesson in to_delete:
                    # ВАЖНО: Сначала логируем изменение, потом удаляем!
                    await db.log_schedule_change(
                        existing_lesson.lesson_id,
                        ChangeType.DELETE,
                        old_data={
                            "name": existing_lesson.name,
                            "teacher": existing_lesson.teacher_name,
                            "subgroup": existing_lesson.subgroup
                        },
                        conn=connection
                    )
                    # Теперь можно безопасно удалить урок
                    await db.delete_lesson(existing_lesson.lesson_id, conn=connection)

                    deleted += 1
                    deleted_details.append({
                        "lesson_id": existing_lesson.lesson_id,
                        "name": existing_lesson.name,
                        "type": existing_lesson.lesson_type,
                        "day": existing_lesson.day_of_week,
                        "number": existing_lesson.lesson_number,
                        "subgroup": existing_lesson.subgroup
                    })

        logger.info(
            "lessons_transaction_completed",
            group_id=group_id,
            week_type=week_type.value,
            added=added,
            updated=updated,
            deleted=deleted,
            added_lessons=_shorten(added_details),
            updated_lessons=_shorten(updated_details),
            deleted_lessons=_shorten(deleted_details),
            duration=round(perf_counter() - phase_started, 4)
        )

        return added, updated, deleted

    if conn is not None:
        return await _process(conn)

    async with db.acquire_connection() as connection:
        return await _process(connection)


async def parse_group(group_id: int) -> ParseResult:
    """
    Парсинг расписания для одной группы.

    Args:
        group_id: ID группы

    Returns:
        ParseResult с результатами парсинга
    """
    start_time = datetime.now()
    timer_start = perf_counter()
    logger.info("parse_group_started", group_id=group_id)

    try:
        db = await get_database()

        # Получаем информацию о группе
        group_info = await db.get_group_info(group_id)
        if not group_info:
            return ParseResult(
                status=False,
                group_id=group_id,
                details="Group not found or inactive",
                errors="GROUP_NOT_FOUND"
            )

        # Загружаем HTML
        html = await fetch_schedule_html(group_info.url)

        # Парсим расписание
        even_lessons, odd_lessons = parse_schedule_html(html, group_id)

        # Обновляем БД в рамках одного соединения
        async with db.acquire_connection() as conn:
            even_added, even_updated, even_deleted = await compare_and_update_lessons(
                db, group_id, even_lessons, WeekType.EVEN, conn=conn
            )

            odd_added, odd_updated, odd_deleted = await compare_and_update_lessons(
                db, group_id, odd_lessons, WeekType.ODD, conn=conn
            )

        # Формируем результат
        total_added = even_added + odd_added
        total_updated = even_updated + odd_updated
        total_deleted = even_deleted + odd_deleted

        duration = (datetime.now() - start_time).total_seconds()

        result = ParseResult(
            status=True,
            group_id=group_id,
            details=f"Successfully parsed schedule for group {group_info.name}",
            lessons_added=total_added,
            lessons_updated=total_updated,
            lessons_deleted=total_deleted
        )

        logger.info(
            "parse_group_completed",
            group_id=group_id,
            duration=duration,
            total_seconds=round(perf_counter() - timer_start, 4),
            added=total_added,
            updated=total_updated,
            deleted=total_deleted
        )

        return result

    except Exception as e:
        logger.error(
            "parse_group_failed",
            group_id=group_id,
            error=str(e),
            exc_info=True
        )
        return ParseResult(
            status=False,
            group_id=group_id,
            details="Parsing failed",
            errors=f"{type(e).__name__}: {str(e)}"
        )


async def parse_groups_batch(group_ids: list[int]) -> list[ParseResult]:
    """
    Парсинг расписания для списка групп параллельно.

    Args:
        group_ids: Список ID групп

    Returns:
        Список результатов парсинга для каждой группы
    """
    config = get_config()
    semaphore = asyncio.Semaphore(config.max_concurrent_parses)

    async def parse_with_semaphore(gid: int) -> ParseResult:
        async with semaphore:
            return await parse_group(gid)

    logger.info("parse_batch_started", total_groups=len(group_ids))

    tasks = [parse_with_semaphore(gid) for gid in group_ids]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    successful = sum(1 for r in results if r.status)
    failed = len(results) - successful

    logger.info(
        "parse_batch_completed",
        total=len(results),
        successful=successful,
        failed=failed
    )

    return results