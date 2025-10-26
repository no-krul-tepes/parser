"""
Утилиты для парсинга расписания.
Содержит функции для обработки текста, времени и других вспомогательных операций.
"""
import logging
import re
import asyncio
from datetime import date, time, timedelta
from dataclasses import dataclass
from typing import Optional, Callable, TypeVar, ParamSpec
import structlog

from .config import get_config

logger = structlog.get_logger()

# Маппинг дней недели
DAY_MAPPING = {
    "пнд": 1,
    "втр": 2,
    "срд": 3,
    "чтв": 4,
    "птн": 5,
    "сбт": 6,
    "вск": 7,
}

# Время начала и окончания пар
LESSON_TIMES = {
    1: (time(9, 0), time(10, 35)),
    2: (time(10, 45), time(12, 20)),
    3: (time(13, 0), time(14, 35)),
    4: (time(14, 45), time(16, 20)),
    5: (time(16, 25), time(18, 0)),
    6: (time(18, 5), time(19, 40)),
}

# Типы занятий
LESSON_TYPE_PREFIXES = {
    "лек.": "Лекция",
    "пр.": "Практика",
    "лаб.": "Лабораторная",
    "сем.": "Семинар",
    "конс.": "Консультация",
}


@dataclass
class LessonInfo:
    """
    Структура с распарсенной информацией об уроке.

    Attributes:
        name: Название дисциплины (без префикса типа занятия)
        lesson_type: Тип занятия (лекция, практика и т.д.)
        teachers: Список преподавателей
        cabinets: Список аудиторий
        subgroup: Номер подгруппы (1, 2) или None
        comment: Дополнительный комментарий (например, "и/д", "и/дэкол")
    """
    name: str
    lesson_type: Optional[str] = None
    teachers: list[str] = None
    cabinets: list[str] = None
    subgroup: Optional[int] = None
    comment: Optional[str] = None

    def __post_init__(self):
        """Инициализация пустых списков."""
        if self.teachers is None:
            self.teachers = []
        if self.cabinets is None:
            self.cabinets = []


def normalize_text(text: str) -> str:
    """
    Нормализация текста: удаление лишних пробелов и спецсимволов.

    Args:
        text: Исходный текст

    Returns:
        Нормализованный текст
    """
    if not text:
        return ""

    # Удаляем неразрывные пробелы и другие невидимые символы
    text = text.replace('\xa0', ' ').replace('\u200b', '')

    # Удаляем множественные пробелы
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_lesson_type(text: str) -> tuple[Optional[str], str]:
    """
    Извлекает тип занятия из текста.

    Args:
        text: Текст с возможным префиксом типа занятия

    Returns:
        Кортеж (тип_занятия, оставшийся_текст)
    """
    text = text.strip()

    for prefix, lesson_type in LESSON_TYPE_PREFIXES.items():
        if text.lower().startswith(prefix):
            return lesson_type, text[len(prefix):].strip()

    return None, text


def extract_subgroup(text: str) -> tuple[Optional[int], str]:
    """
    Извлекает номер подгруппы из текста.

    Поддерживаемые форматы:
    - "1 п/г", "2 п/г"
    - "- 1 п/г", "- 2 п/г"
    - "1п/г", "2п/г"

    Args:
        text: Текст с возможным указанием подгруппы

    Returns:
        Кортеж (номер_подгруппы, текст_без_подгруппы)
    """
    # Паттерн для поиска подгруппы
    subgroup_pattern = r'[-\s]*(\d)\s*п/г'
    match = re.search(subgroup_pattern, text, re.IGNORECASE)

    if match:
        subgroup_num = int(match.group(1))
        if subgroup_num in (1, 2):
            # Удаляем найденный паттерн из текста
            text_without_subgroup = text[:match.start()] + text[match.end():]
            return subgroup_num, text_without_subgroup.strip()

    return None, text

def extract_teachers_and_cabinets(text: str) -> tuple[list[str], list[str], str]:
    """
    Извлекает преподавателей и аудитории из текста.

    ВАЖНО: Порядок обработки критичен!
    1. Извлекаем отдельные комментарии (не слитые с аудиториями)
    2. Извлекаем ФИО преподавателей (чтобы их инициалы не спутать с аудиториями)
    3. Извлекаем аудитории (с прилипшими комментариями)
    4. Оставшееся - название

    Примеры:
    - "Гидрогеология ПЛЮСНИН А.М. а.8228 и/д"
      -> name="Гидрогеология", teachers=["ПЛЮСНИН А.М."], cabinets=["а.8228"]
    - "Информатика ЦЫРЕНОВА АЮ.А а.1-17д/кл"
      -> name="Информатика", teachers=["ЦЫРЕНОВА А.Ю.А."], cabinets=["а.1-17д/кл"]
    - "Русский язык АНГАРХАЕВА Ю.П. а.0425и/д"
      -> name="Русский язык", teachers=["АНГАРХАЕВА Ю.П."], cabinets=["а.0425и/д"]

    Args:
        text: Текст с информацией о преподавателях и аудиториях

    Returns:
        Кортеж (список_преподавателей, список_аудиторий, оставшийся_текст)
    """
    teachers = []
    cabinets = []

    # ЭТАП 0: Извлекаем ОТДЕЛЬНЫЕ комментарии (не трогаем слитые с аудиториями)
    comment, text_without_comment = extract_comment(text)

    working_text = text_without_comment

    # ЭТАП 1: Извлекаем ФИО (ВАЖНО: делаем это ДО извлечения аудиторий!)
    # Паттерн для ФИО в КАПСЕ: ФАМИЛИЯ пробел ИНИЦИАЛЫ
    # ФАМИЛИЯ - заглавные буквы (может быть с дефисом)
    # ИНИЦИАЛЫ - различные варианты:
    #   1) И.О. (стандарт: Б.В., А.М.)
    #   2) ИО.И (слипшиеся: АЮ.А)
    #   3) И.О (без точки в конце: А.В)

    # Расширенный паттерн для инициалов
    teacher_pattern = r'[А-ЯЁ]+(?:-[А-ЯЁ]+)?\s+(?:[А-ЯЁ]{1,2}\.?[А-ЯЁ]\.?)'

    teacher_matches = list(re.finditer(teacher_pattern, working_text))
    for match in reversed(teacher_matches):  # Удаляем с конца
        teacher = match.group(0).strip()

        # Нормализуем инициалы: добавляем точки если их нет
        teacher = normalize_teacher_name(teacher)

        teachers.insert(0, teacher)
        # Удаляем из текста, заменяя пробелом
        working_text = working_text[:match.start()] + ' ' + working_text[match.end():]

    # ЭТАП 2: Извлекаем аудитории (после того как убрали ФИО)
    # Паттерн для аудитории с возможными СЛИТЫМИ комментариями
    # Примеры:
    #   - а.0426
    #   - а.1-17д/кл (с комментарием /кл)
    #   - а.0425и/д (с комментарием и/д)
    #   - а.8240эбж (с комментарием эбж)
    #   - а.726-2 ТМиОК (ТМиОК отдельно, не включается)

    # Расширенный паттерн: аудитория может содержать буквы, цифры, дефисы и слитые комментарии
    cabinet_pattern = r'а\.[\dа-яА-Я\-]+(?:/[а-яА-Я]+|и/д(?:экол)?|эбж|экол)?'

    cabinet_matches = list(re.finditer(cabinet_pattern, working_text, re.IGNORECASE))
    for match in reversed(cabinet_matches):  # Удаляем с конца
        cabinet = match.group(0)
        cabinets.insert(0, cabinet)
        # Удаляем из текста, заменяя пробелом
        working_text = working_text[:match.start()] + ' ' + working_text[match.end():]

    # ЭТАП 3: Очищаем оставшийся текст
    # Удаляем дефисы, которые использовались как разделители
    working_text = re.sub(r'\s*-\s*', ' ', working_text)
    # Удаляем множественные пробелы
    working_text = re.sub(r'\s+', ' ', working_text).strip()

    return teachers, cabinets, working_text


def normalize_teacher_name(name: str) -> str:
    """
    Нормализует ФИО преподавателя - расставляет точки в инициалах.

    Примеры:
    - "ЦЫРЕНОВА АЮ.А" -> "ЦЫРЕНОВА А.Ю.А."
    - "МИХЕЕВ Б.В." -> "МИХЕЕВ Б.В."
    - "БЫКОВ АВ" -> "БЫКОВ А.В."
    - "ПЛЮСНИН А.М" -> "ПЛЮСНИН А.М."

    Args:
        name: ФИО в формате "ФАМИЛИЯ ИНИЦИАЛЫ"

    Returns:
        Нормализованное ФИО
    """
    if not name:
        return name

    # Разделяем на фамилию и инициалы
    parts = name.split(maxsplit=1)
    if len(parts) != 2:
        return name

    surname, initials = parts

    # Убираем все точки из инициалов
    initials_clean = initials.replace('.', '')

    # Если инициалы - это 2-3 заглавные буквы, расставляем точки
    if re.match(r'^[А-ЯЁ]{2,3}$', initials_clean):
        # "АЮА" -> "А.Ю.А."
        formatted = '.'.join(initials_clean) + '.'
        return f"{surname} {formatted}"

    # Если инициалы уже с точками, но возможно не все
    # "А.М" -> "А.М.", "АЮ.А" -> "А.Ю.А."
    initials_normalized = re.sub(r'([А-ЯЁ])(?=[А-ЯЁ])', r'\1.', initials_clean)
    if not initials_normalized.endswith('.'):
        initials_normalized += '.'

    return f"{surname} {initials_normalized}"


def extract_comment(text: str) -> tuple[Optional[str], str]:
    """
    Извлекает ОТДЕЛЬНЫЕ комментарии из текста (например, "и/д", "и/дэкол").

    ВАЖНО: Не трогает комментарии, слитые с аудиториями (а.123и/д)!
    Такие комментарии останутся частью номера аудитории.

    Args:
        text: Текст с возможным комментарием

    Returns:
        Кортеж (комментарий, текст_без_комментария)
    """
    # Паттерны для ОТДЕЛЬНО СТОЯЩИХ комментариев
    # Важно: должны быть окружены пробелами или быть в конце строки
    comment_patterns = [
        r'\s+и/д(?:экол)?\s*',  # и/д, и/дэкол (отдельно)
        r'\s+эбж\s*',  # эбж (отдельно)
        r'\s+экол\s*',  # экол (отдельно)
        r'\s+ТМиОК\s*',  # ТМиОК (отдельно)
        r'\(.*?\)',  # Текст в скобках
    ]

    comments = []
    working_text = text

    for pattern in comment_patterns:
        matches = list(re.finditer(pattern, working_text, re.IGNORECASE))
        for match in reversed(matches):  # Удаляем с конца
            comment = match.group(0).strip()
            comments.append(comment)
            working_text = working_text[:match.start()] + ' ' + working_text[match.end():]

    # Объединяем все комментарии
    combined_comment = ' '.join(reversed(comments)) if comments else None

    return combined_comment, working_text.strip()


def clean_discipline_name(name: str) -> str:
    """
    Очищает название дисциплины от артефактов парсинга.

    Убирает:
    - Лишние точки в конце
    - Одинокие инициалы
    - Множественные пробелы
    - ОТДЕЛЬНЫЕ комментарии (но не слитые с аудиториями!)

    Args:
        name: Название дисциплины

    Returns:
        Очищенное название
    """
    if not name:
        return name

    # Убираем ОТДЕЛЬНЫЕ комментарии в конце названия
    # Важно: они уже должны быть удалены, но на всякий случай
    name = re.sub(r'\s+(?:эбж|экол|ТМиОК)$', '', name, flags=re.IGNORECASE)

    # Убираем одинокие точки в конце (артефакты от инициалов)
    name = re.sub(r'\s+\.$', '', name)

    # Убираем одинокие инициалы (например " А." или " И.О." или " АЮ.А")
    name = re.sub(r'\s+[А-ЯЁ]{1,3}\.?(?:[А-ЯЁ]\.?)?$', '', name)

    # Убираем слитые комментарии, если они случайно попали в название
    # (не должно происходить, но на всякий случай)
    name = re.sub(r'/[а-яА-Я]+$', '', name)
    name = re.sub(r'и/д(?:экол)?$', '', name, flags=re.IGNORECASE)

    # Убираем множественные пробелы
    name = re.sub(r'\s+', ' ', name)

    return name.strip()


def parse_lesson_info(raw_text: str) -> LessonInfo:
    """
    Парсит сырой текст урока в структурированный объект.

    Последовательность парсинга:
    1. Извлекаем тип занятия (лек., пр., лаб.)
    2. Извлекаем подгруппу (1 п/г, 2 п/г)
    3. Извлекаем преподавателей и аудитории (преподаватели СНАЧАЛА!)
       - Аудитории могут содержать слитые комментарии (а.123и/д, а.456/кл)
    4. Оставшийся текст = название дисциплины

    Args:
        raw_text: Сырой текст из HTML ячейки

    Returns:
        LessonInfo с распарсенными данными
    """
    if not raw_text or raw_text.strip() in ('_', ''):
        return LessonInfo(name="")

    text = normalize_text(raw_text)

    # 1. Извлекаем тип занятия
    lesson_type, text = extract_lesson_type(text)

    # 2. Извлекаем подгруппу
    subgroup, text = extract_subgroup(text)

    # 3. Извлекаем преподавателей, аудитории; оставшееся - название
    teachers, cabinets, lesson_name = extract_teachers_and_cabinets(text)

    # 4. Очищаем название от артефактов
    lesson_name = clean_discipline_name(lesson_name)

    # 5. Если название пустое, но есть данные, логируем предупреждение
    if not lesson_name and (teachers or cabinets):
        logger.warning(
            "lesson_name_empty",
            raw_text=raw_text,
            teachers=teachers,
            cabinets=cabinets
        )
        # В крайнем случае используем весь текст как название
        lesson_name = text

    return LessonInfo(
        name=lesson_name,
        lesson_type=lesson_type,
        teachers=teachers,
        cabinets=cabinets,
        subgroup=subgroup,
        comment=None
    )

def parse_lesson_info_with_subgroups(raw_text: str) -> list[LessonInfo]:
    """
    Парсит сырой текст урока, поддерживая множественные подгруппы.

    Если в тексте указаны разные данные для разных подгрупп,
    возвращает список LessonInfo для каждой подгруппы отдельно.

    Примеры:
    - "Информатика- 1 п/г ПАВЛОВА И.А. а.15-357-2" -> одна запись с subgroup=1
    - "Информатика- 2 п/г ЦЫРЕНОВА АЮ.А а.1-17д/кл" -> одна запись с subgroup=2
    - "Иностранный язык- 1 п/г ДАНЗАНОВА С.В. а.719 2 п/г БАЗАРОВА М.Д. а.0300"
      -> две записи с разными подгруппами

    Args:
        raw_text: Сырой текст из HTML ячейки

    Returns:
        Список LessonInfo (обычно один элемент, несколько если есть разделение по подгруппам)
    """
    if not raw_text or raw_text.strip() in ('_', ''):
        return [LessonInfo(name="")]

    text = normalize_text(raw_text)

    # Проверяем, есть ли явное разделение по подгруппам
    # Ищем паттерн: "... 1 п/г ... 2 п/г ..."
    subgroup_divider_pattern = r'[-\s]*(\d)\s*п/г'
    subgroup_matches = list(re.finditer(subgroup_divider_pattern, text, re.IGNORECASE))

    # Если нашли несколько упоминаний подгрупп, проверяем разные ли они
    if len(subgroup_matches) > 1:
        subgroup_numbers = [int(m.group(1)) for m in subgroup_matches]
        # Если подгруппы разные, разбиваем на несколько записей
        if len(set(subgroup_numbers)) > 1:
            lesson_infos = []

            # Извлекаем тип занятия из начала (общий для всех)
            lesson_type, text_without_type = extract_lesson_type(text)

            # Извлекаем базовое название (часть до первой подгруппы)
            base_name_part = text_without_type[:subgroup_matches[0].start()].strip()
            # Удаляем из базового названия возможные ФИО и аудитории
            _, _, base_name = extract_teachers_and_cabinets(base_name_part)
            base_name = clean_discipline_name(base_name)

            # Разбиваем по подгруппам
            for i, match in enumerate(subgroup_matches):
                subgroup_num = int(match.group(1))

                # Определяем границы текста для этой подгруппы
                start_pos = match.end()  # После маркера подгруппы
                end_pos = subgroup_matches[i + 1].start() if i + 1 < len(subgroup_matches) else len(text_without_type)

                subgroup_text = text_without_type[start_pos:end_pos].strip()

                # Парсим для конкретной подгруппы
                teachers, cabinets, lesson_name = extract_teachers_and_cabinets(subgroup_text)
                lesson_name = clean_discipline_name(lesson_name)

                # Если название пустое, используем базовое
                if not lesson_name:
                    lesson_name = base_name

                lesson_infos.append(LessonInfo(
                    name=lesson_name,
                    lesson_type=lesson_type,
                    teachers=teachers,
                    cabinets=cabinets,
                    subgroup=subgroup_num,
                    comment=None
                ))

            return lesson_infos

    # Обычный случай - одна подгруппа или без подгрупп
    lesson_info = parse_lesson_info(raw_text)
    return [lesson_info]


def get_monday_of_week(target_date: date, week_type: Optional[str] = None) -> date:
    """
    Получить дату понедельника для заданной даты с учетом типа недели.

    Args:
        target_date: Целевая дата
        week_type: Тип недели ("even" или "odd"). Если указан, находит ближайший
                   понедельник с таким типом недели

    Returns:
        Дата понедельника
    """
    # Находим понедельник текущей недели
    days_since_monday = target_date.weekday()
    monday = target_date - timedelta(days=days_since_monday)

    # Если нужен конкретный тип недели, корректируем
    if week_type is not None:
        current_week_type = get_week_type_for_date(monday)
        if current_week_type != week_type:
            # Сдвигаем на неделю вперед
            monday = monday + timedelta(days=7)

    return monday


def get_academic_year(target_date: date) -> tuple[int, int]:
    """
    Получить учебный год для заданной даты.

    Args:
        target_date: Целевая дата

    Returns:
        Кортеж (начальный_год, конечный_год), например (2024, 2025)
    """
    year = target_date.year
    if target_date.month < 9:
        return (year - 1, year)
    return (year, year + 1)


def get_academic_year_start(target_date: date) -> date:
    """
    Получить дату начала учебного года (1 сентября) для заданной даты.

    Args:
        target_date: Целевая дата

    Returns:
        Дата 1 сентября соответствующего учебного года
    """
    year = target_date.year
    if target_date.month < 9:
        year -= 1
    return date(year, 9, 1)


def get_week_type_for_date(target_date: date) -> str:
    """
    Определить тип недели для конкретной даты по учебному календарю.

    Правило: неделя, которая содержит 1-7 сентября, считается нечетной (первой),
    далее недели чередуются.

    Args:
        target_date: Дата для определения типа недели

    Returns:
        "even" или "odd"
    """
    # Определяем начало учебного года (1 сентября)
    year = target_date.year

    # Если мы до сентября, то это предыдущий учебный год
    if target_date.month < 9:
        year -= 1

    # Первое сентября текущего учебного года
    academic_year_start = date(year, 9, 1)

    # Если дата раньше начала учебного года, возвращаем odd
    if target_date < academic_year_start:
        return "odd"

    # Находим понедельник недели, содержащей 1 сентября
    # Это будет начало первой учебной недели
    sept_1_weekday = academic_year_start.weekday()  # 0=понедельник, 6=воскресенье
    first_week_monday = academic_year_start - timedelta(days=sept_1_weekday)

    # Вычисляем количество полных недель от начала первой учебной недели
    days_diff = (target_date - first_week_monday).days
    week_number = (days_diff // 7) + 1

    # Первая неделя (содержащая 1-7 сентября) - нечетная
    week_type = "even" if week_number % 2 == 0 else "odd"

    logger.debug(
        "week_type_calculated",
        target_date=target_date.isoformat(),
        academic_year_start=academic_year_start.isoformat(),
        first_week_monday=first_week_monday.isoformat(),
        days_diff=days_diff,
        week_number=week_number,
        week_type=week_type
    )

    return week_type


def get_current_week_type() -> str:
    """
    Определить тип текущей недели (четная/нечетная) по учебному календарю.

    Returns:
        "even" или "odd"
    """
    today = date.today()
    return get_week_type_for_date(today)


def get_week_number_in_academic_year(target_date: date) -> int:
    """
    Получить номер учебной недели в учебном году.

    Args:
        target_date: Целевая дата

    Returns:
        Номер недели (начиная с 1 для первой недели)
    """
    academic_year_start = get_academic_year_start(target_date)
    sept_1_weekday = academic_year_start.weekday()
    first_week_monday = academic_year_start - timedelta(days=sept_1_weekday)

    days_diff = (target_date - first_week_monday).days
    week_number = (days_diff // 7) + 1

    return max(1, week_number)


def is_academic_year_active(target_date: date) -> bool:
    """
    Проверить, является ли дата частью активного учебного года.

    Учебный год обычно длится с сентября по июнь.

    Args:
        target_date: Целевая дата

    Returns:
        True если дата в пределах учебного года
    """
    month = target_date.month
    # Учебный год: сентябрь-июнь (месяцы 9-12 и 1-6)
    return month >= 9 or month <= 6


def format_academic_year(target_date: date) -> str:
    """
    Форматировать учебный год в читаемый вид.

    Args:
        target_date: Целевая дата

    Returns:
        Строка вида "2024/2025"
    """
    start_year, end_year = get_academic_year(target_date)
    return f"{start_year}/{end_year}"


# Типы для generic retry функции
P = ParamSpec('P')
T = TypeVar('T')


async def retry_async(
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs
) -> T:
    """
    Повторяет асинхронную функцию при ошибках с экспоненциальной задержкой.

    Args:
        func: Асинхронная функция для выполнения
        *args: Позиционные аргументы для функции
        **kwargs: Именованные аргументы для функции

    Returns:
        Результат выполнения функции

    Raises:
        Exception: Последнее исключение после всех попыток
    """
    config = get_config()
    last_exception = None

    for attempt in range(1, config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = config.retry_delay * (config.retry_exponential_base ** (attempt - 1))
                logger.warning(
                    "retry_attempt",
                    attempt=attempt,
                    max_retries=config.max_retries,
                    delay=delay,
                    error=str(e)
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "retry_exhausted",
                    attempts=config.max_retries,
                    error=str(e)
                )

    raise last_exception


def format_lesson_time(start: time, end: time) -> str:
    """
    Форматирует время урока в читаемый вид.

    Args:
        start: Время начала
        end: Время окончания

    Returns:
        Строка вида "09:00-10:35"
    """
    return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"


def format_day_name(day_of_week: int, full: bool = False) -> str:
    """
    Форматирует номер дня недели в название.

    Args:
        day_of_week: Номер дня недели (1-7)
        full: Если True, возвращает полное название, иначе сокращенное

    Returns:
        Название дня недели
    """
    day_names_full = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье",
    }

    day_names_short = {
        1: "Пнд",
        2: "Втр",
        3: "Срд",
        4: "Чтв",
        5: "Птн",
        6: "Сбт",
        7: "Вск",
    }

    names = day_names_full if full else day_names_short
    return names.get(day_of_week, "Неизвестно")


def validate_lesson_data(lesson_info: LessonInfo) -> tuple[bool, Optional[str]]:
    """
    Валидирует данные урока.

    Args:
        lesson_info: Информация об уроке

    Returns:
        Кортеж (валидность, сообщение_об_ошибке)
    """
    if not lesson_info.name:
        return False, "Отсутствует название дисциплины"

    if lesson_info.subgroup and lesson_info.subgroup not in (1, 2):
        return False, f"Некорректный номер подгруппы: {lesson_info.subgroup}"

    return True, None


def configure_logging(log_level: str = "INFO") -> None:
    """
    Настройка structlog для логирования.

    Args:
        log_level: Уровень логирования
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )