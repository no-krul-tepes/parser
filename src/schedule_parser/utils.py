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


def extract_comment(text: str) -> tuple[Optional[str], str]:
    """
    Извлекает комментарии из текста (например, "и/д", "и/дэкол").

    Args:
        text: Текст с возможным комментарием

    Returns:
        Кортеж (комментарий, текст_без_комментария)
    """
    # Паттерны для комментариев (должны быть в конце или рядом с аудиторией)
    comment_patterns = [
        r'и/д(?:экол)?',  # и/д, и/дэкол
        r'\(.*?\)',  # Текст в скобках
    ]

    for pattern in comment_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            comment = match.group(0)
            text_without_comment = text[:match.start()] + text[match.end():]
            return comment, text_without_comment.strip()

    return None, text


def extract_teachers_and_cabinets(text: str) -> tuple[list[str], list[str], str]:
    """
    Извлекает преподавателей и аудитории из текста.

    Стратегия парсинга:
    1. Извлекаем комментарии (и/д, и/дэкол)
    2. Ищем все аудитории (паттерн а.XXXX)
    3. Ищем все ФИО (ФАМИЛИЯ И.О. в КАПСЕ)
    4. Оставшийся текст - название дисциплины

    Примеры:
    - "Математика ИВАНОВ И.И. а.101" -> name="Математика", teachers=["ИВАНОВ И.И."], cabinets=["а.101"]
    - "История МИХЕЕВ Б.В. а.0426" -> name="История", teachers=["МИХЕЕВ Б.В."], cabinets=["а.0426"]

    Args:
        text: Текст с информацией о преподавателях и аудиториях

    Returns:
        Кортеж (список_преподавателей, список_аудиторий, оставшийся_текст)
    """
    teachers = []
    cabinets = []

    # Сначала извлекаем комментарии (и/д, и/дэкол)
    comment, text_without_comment = extract_comment(text)

    # Паттерн для аудитории: а.XXXX с возможными буквами и дефисами
    # Примеры: а.0426, а.15-466, а.9-Спорт1, а.728-3, а.0316и
    cabinet_pattern = r'а\.[\dа-яА-Я\-]+'

    # Паттерн для ФИО в КАПСЕ: ФАМИЛИЯ пробел И.О.
    # ФАМИЛИЯ - заглавные буквы (может быть с дефисом)
    # И.О. - заглавная буква + точка, еще раз заглавная + точка
    # Примеры: МИХЕЕВ Б.В., ФЕДОРОВА И.Э., ГЕРГЕНОВА Н.Д., ШАНТАГАРОВА Н.В.
    teacher_pattern = r'[А-ЯЁ]+(?:-[А-ЯЁ]+)?\s+[А-ЯЁ]\.[А-ЯЁ]\.'

    # Работаем с текстом без комментариев
    working_text = text_without_comment

    # 1. Находим и извлекаем все аудитории
    cabinet_matches = list(re.finditer(cabinet_pattern, working_text, re.IGNORECASE))
    for match in reversed(cabinet_matches):  # Удаляем с конца
        cabinet = match.group(0)
        # Очищаем от артефактов (и/д уже убрали выше)
        cabinets.insert(0, cabinet)
        # Удаляем из текста, заменяя пробелом
        working_text = working_text[:match.start()] + ' ' + working_text[match.end():]

    # 2. Находим и извлекаем всех преподавателей
    teacher_matches = list(re.finditer(teacher_pattern, working_text))
    for match in reversed(teacher_matches):  # Удаляем с конца
        teacher = match.group(0).strip()
        teachers.insert(0, teacher)
        # Удаляем из текста, заменяя пробелом
        working_text = working_text[:match.start()] + ' ' + working_text[match.end():]

    # 3. Очищаем оставшийся текст
    # Удаляем дефисы, которые использовались как разделители
    working_text = re.sub(r'\s*-\s*', ' ', working_text)
    # Удаляем множественные пробелы
    working_text = re.sub(r'\s+', ' ', working_text).strip()

    return teachers, cabinets, working_text

def parse_lesson_info(raw_text: str) -> LessonInfo:
    """
    Парсит сырой текст урока в структурированный объект.

    Последовательность парсинга:
    1. Извлекаем тип занятия (лек., пр., лаб.)
    2. Извлекаем подгруппу (1 п/г, 2 п/г)
    3. Извлекаем преподавателей, аудитории и комментарии
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

    # 4. Если название пустое, но есть данные, логируем предупреждение
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
        comment=None  # Комментарии уже учтены в обработке аудиторий
    )


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