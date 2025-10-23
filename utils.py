"""
Вспомогательные функции и утилиты для парсинга расписания.
Улучшенная версия с обработкой всех edge cases.
"""

import asyncio
import logging
import re
from datetime import date, time, timedelta
from typing import Optional, Callable, TypeVar, Any
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()

T = TypeVar('T')

# Маппинг дней недели из сокращений
DAY_MAPPING = {
    "пнд": 1,
    "втр": 2,
    "срд": 3,
    "чтв": 4,
    "птн": 5,
    "сбт": 6,
}

# Стандартное расписание звонков
LESSON_TIMES = {
    1: (time(9, 0), time(10, 35)),
    2: (time(10, 45), time(12, 20)),
    3: (time(13, 0), time(14, 35)),
    4: (time(14, 45), time(16, 20)),
    5: (time(16, 25), time(18, 0)),
    6: (time(18, 5), time(19, 40)),
}


@dataclass
class LessonInfo:
    """Структурированная информация об уроке."""
    lesson_type: Optional[str] = None  # лек, пр, лаб
    name: Optional[str] = None
    teachers: list[str] = None  # Список преподавателей
    cabinets: list[str] = None  # Список аудиторий
    subgroup: Optional[int] = None  # Номер подгруппы (1 или 2)
    comment: Optional[str] = None  # Комментарии типа "и/дэкол"

    def __post_init__(self):
        if self.teachers is None:
            self.teachers = []
        if self.cabinets is None:
            self.cabinets = []


# Компилируем regex-паттерны один раз для производительности
class LessonPatterns:
    """Скомпилированные regex-паттерны для парсинга."""

    # Тип занятия в начале
    LESSON_TYPE = re.compile(r'^(лек|пр|лаб)\.')

    # Подгруппа в названии: "- 1 п/г" или "-1п/г"
    SUBGROUP = re.compile(r'-\s*(\d)\s*п/г')

    # Комментарий в конце (и/д, и/дэкол и т.п.)
    COMMENT_SUFFIX = re.compile(r'\s+(и/д\S*)$')

    # Множественные преподаватели через много пробелов
    # Формат: "ИМЯ1 И.О.   ИМЯ2 И.О. - а.XXX"
    MULTIPLE_TEACHERS = re.compile(
        r'\s{2,}([А-ЯЁ]+(?:\s+[А-ЯЁ]\.(?:\s*[А-ЯЁ]\.)?)?)\s+-\s+а\.([^\s]+)'
    )

    # Основная аудитория
    CABINET = re.compile(r'\s+а\.([^\s]+)')

    # Множественные пробелы
    MULTIPLE_SPACES = re.compile(r'\s{2,}')


def normalize_text(text: str) -> str:
    """
    Нормализация текста: удаление лишних пробелов и символов.

    Args:
        text: Исходный текст

    Returns:
        Нормализованный текст

    Examples:
        >>> normalize_text("История  МИХЕЕВ Б.В.   а.0426")
        'История МИХЕЕВ Б.В. а.0426'
    """
    # Удаляем начальные/конечные пробелы
    text = text.strip()
    return text


def extract_lesson_type(text: str) -> tuple[Optional[str], str]:
    """
    Извлечь тип занятия из начала текста.

    Args:
        text: Текст урока

    Returns:
        Кортеж (тип_занятия, оставшийся_текст)

    Examples:
        >>> extract_lesson_type("лек.История МИХЕЕВ Б.В.")
        ('лек', 'История МИХЕЕВ Б.В.')
        >>> extract_lesson_type("История МИХЕЕВ Б.В.")
        (None, 'История МИХЕЕВ Б.В.')
    """
    match = LessonPatterns.LESSON_TYPE.match(text)
    if match:
        lesson_type = match.group(1)
        remaining = text[match.end():].strip()
        return lesson_type, remaining
    return None, text


def extract_comment_suffix(text: str) -> tuple[Optional[str], str]:
    """
    Извлечь комментарий из конца текста.

    Args:
        text: Текст урока

    Returns:
        Кортеж (комментарий, оставшийся_текст)

    Examples:
        >>> extract_comment_suffix("Основы безопасности ШАНТАГАРОВА Н.В. а.8236 и/дэкол")
        ('и/дэкол', 'Основы безопасности ШАНТАГАРОВА Н.В. а.8236')
    """
    match = LessonPatterns.COMMENT_SUFFIX.search(text)
    if match:
        comment = match.group(1)
        remaining = text[:match.start()].strip()
        return comment, remaining
    return None, text


def extract_subgroup(text: str) -> tuple[Optional[int], str]:
    """
    Извлечь номер подгруппы из названия.

    Args:
        text: Название дисциплины

    Returns:
        Кортеж (номер_подгруппы, название_без_подгруппы)

    Examples:
        >>> extract_subgroup("Информатика- 1 п/г")
        (1, 'Информатика')
        >>> extract_subgroup("Информатика- 2 п/г")
        (2, 'Информатика')
        >>> extract_subgroup("Информатика")
        (None, 'Информатика')
    """
    match = LessonPatterns.SUBGROUP.search(text)
    if match:
        subgroup = int(match.group(1))
        # Удаляем подгруппу из названия, убирая также лишний дефис
        remaining = text[:match.start()].rstrip('- ')
        return subgroup, remaining
    return None, text


def extract_multiple_teachers_cabinets(text: str) -> tuple[list[tuple[str, str]], str]:
    """
    Извлечь множественных преподавателей с их аудиториями.

    Формат: "...   ПРЕПОДАВАТЕЛЬ2 - а.АУДИТОРИЯ2   ПРЕПОДАВАТЕЛЬ3 - а.АУДИТОРИЯ3"

    Args:
        text: Текст урока

    Returns:
        Кортеж (список_пар_(преподаватель, аудитория), оставшийся_текст)

    Examples:
        >>> extract_multiple_teachers_cabinets("Иностранный язык ДАНЗАНОВА С.В. а.0107   БАЗАРОВА М.Д. - а.718а")
        ([('БАЗАРОВА М.Д.', '718а')], 'Иностранный язык ДАНЗАНОВА С.В. а.0107')
    """
    teachers_cabinets = []
    remaining = text

    # Находим все совпадения с конца (идём справа налево)
    matches = list(LessonPatterns.MULTIPLE_TEACHERS.finditer(text))

    if matches:
        # Обрабатываем совпадения
        for match in matches:
            teacher = match.group(1).strip()
            cabinet = match.group(2).strip()
            teachers_cabinets.append((teacher, cabinet))

        # Удаляем все найденные совпадения из текста
        # Берём начало до первого совпадения
        remaining = text[:matches[0].start()].strip()

    return teachers_cabinets, remaining


def extract_cabinet(text: str) -> tuple[Optional[str], str]:
    """
    Извлечь основную аудиторию из текста.

    Args:
        text: Текст урока

    Returns:
        Кортеж (аудитория, оставшийся_текст)

    Examples:
        >>> extract_cabinet("История МИХЕЕВ Б.В. а.0426")
        ('0426', 'История МИХЕЕВ Б.В.')
        >>> extract_cabinet("История МИХЕЕВ Б.В. а.0316и/д")
        ('0316и/д', 'История МИХЕЕВ Б.В.')
    """
    match = LessonPatterns.CABINET.search(text)
    if match:
        cabinet = match.group(1)
        # Удаляем аудиторию из текста
        remaining = text[:match.start()] + text[match.end():]
        remaining = remaining.strip()
        return cabinet, remaining
    return None, text


def extract_teacher(text: str) -> tuple[Optional[str], str]:
    """
    Извлечь преподавателя из текста.

    Ищем паттерн заглавных букв в конце или перед аудиторией.

    Args:
        text: Текст урока (после удаления аудитории)

    Returns:
        Кортеж (преподаватель, название_дисциплины)

    Examples:
        >>> extract_teacher("История МИХЕЕВ Б.В.")
        ('МИХЕЕВ Б.В.', 'История')
        >>> extract_teacher("Физическая культура и спорт ФКС 21")
        ('ФКС 21', 'Физическая культура и спорт')
    """
    # Нормализуем пробелы перед поиском
    text = re.sub(r'\s+', ' ', text).strip()

    # Улучшенный паттерн для поиска преподавателя
    # Преподаватель: ФАМИЛИЯ (все заглавные буквы) + опционально инициалы
    # Формат: ФАМИЛИЯ И.О. или ФАМИЛИЯ И. или просто ФАМИЛИЯ
    teacher_pattern = re.compile(
        r'\s+([А-ЯЁ]+(?:-[А-ЯЁ]+)*'  # Фамилия (все заглавные, может быть с дефисом)
        r'(?:\s+[А-ЯЁ]\.[А-ЯЁ]\.|\s+[А-ЯЁ]\.)?)$'  # Инициалы (опционально)
    )

    match = teacher_pattern.search(text)
    if match:
        teacher = match.group(1).strip()
        # Проверяем, что это похоже на имя преподавателя (больше 2 букв или есть точка)
        if len(teacher) > 2 or '.' in teacher:
            remaining = text[:match.start()].strip()
            return teacher, remaining

    # Если не нашли паттерн с инициалами, ищем просто заглавное слово в конце
    # Это для случаев типа "ФКС 21"
    simple_pattern = re.compile(r'\s+([А-ЯЁ]{2,}(?:\s+\d+)?)$')
    match = simple_pattern.search(text)
    if match:
        teacher = match.group(1).strip()
        remaining = text[:match.start()].strip()
        return teacher, remaining

    return None, text


def parse_lesson_info(raw_text: str) -> LessonInfo:
    """
    Комплексное извлечение информации об уроке из сырого текста.

    Обрабатывает все edge cases:
    - Множественные преподаватели и аудитории
    - Подгруппы
    - Комментарии
    - Разные типы занятий
    - Отсутствующие данные

    Args:
        raw_text: Сырой текст из HTML

    Returns:
        LessonInfo с извлечёнными данными

    Examples:
        >>> info = parse_lesson_info("лек.История МИХЕЕВ Б.В. а.0426")
        >>> (info.lesson_type, info.name, info.teachers[0], info.cabinets[0])
        ('лек', 'История', 'МИХЕЕВ Б.В.', '0426')

        >>> info = parse_lesson_info("лаб.Информатика- 1 п/г ПАВЛОВА И.А. а.15-357-2")
        >>> (info.name, info.subgroup, info.teachers[0])
        ('Информатика', 1, 'ПАВЛОВА И.А.')

        >>> info = parse_lesson_info("пр.Иностранный язык ДАНЗАНОВА С.В. а.0107   БАЗАРОВА М.Д. - а.718а")
        >>> len(info.teachers), len(info.cabinets)
        (2, 2)
    """
    text = normalize_text(raw_text)

    # Пустой урок
    if text == '_' or not text:
        return LessonInfo()

    result = LessonInfo()

    # 1. Извлекаем тип занятия
    result.lesson_type, text = extract_lesson_type(text)

    # 2. Извлекаем комментарий в конце
    result.comment, text = extract_comment_suffix(text)

    # 3. Извлекаем множественных преподавателей и их аудитории (до основной аудитории!)
    multiple_teachers_cabinets, text = extract_multiple_teachers_cabinets(text)

    # Добавляем множественных преподавателей
    for teacher, cabinet in multiple_teachers_cabinets:
        result.teachers.append(teacher)
        result.cabinets.append(cabinet)

    # 4. Извлекаем основную аудиторию
    main_cabinet, text = extract_cabinet(text)

    # 5. Извлекаем основного преподавателя (ПОСЛЕ удаления аудитории, но ДО подгруппы!)
    # Теперь в text остался только: "Название ПРЕПОДАВАТЕЛЬ"
    main_teacher, text = extract_teacher(text)

    # Добавляем основного преподавателя и аудиторию в начало списков
    # (чтобы основные данные были первыми)
    if main_teacher:
        result.teachers.insert(0, main_teacher)
    if main_cabinet:
        result.cabinets.insert(0, main_cabinet)

    # 6. Извлекаем подгруппу из оставшегося текста (название)
    result.subgroup, text = extract_subgroup(text)

    # 7. Оставшийся текст - это название дисциплины
    # Нормализуем множественные пробелы и убираем лишние пробелы
    result.name = LessonPatterns.MULTIPLE_SPACES.sub(' ', text).strip() if text else None

    return result


def get_week_type_for_date(target_date: date) -> str:
    """
    Определение типа недели по учебному году.

    Считаем, что отсчет ведется от недели 1-7 сентября как нечетной,
    далее недели чередуются.

    Args:
        target_date: Дата для определения типа недели

    Returns:
        "even" или "odd"
    """
    academic_year = target_date.year
    if target_date.month < 9:
        academic_year -= 1

    start_week = date(academic_year, 9, 1)
    start_weekday = start_week.weekday()
    if start_weekday != 0:
        days_to_monday = (7 - start_weekday) % 7
        if days_to_monday == 0:
            days_to_monday = 7
        start_week_monday = start_week - timedelta(days=start_weekday)
    else:
        start_week_monday = start_week

    days_diff = (target_date - start_week_monday).days
    week_number = days_diff // 7

    is_odd = week_number % 2 == 0
    return "odd" if is_odd else "even"


def get_monday_of_week(target_date: date) -> date:
    """
    Получить понедельник недели для заданной даты.

    Args:
        target_date: Дата

    Returns:
        Дата понедельника той же недели
    """
    days_to_monday = target_date.weekday()
    return target_date - timedelta(days=days_to_monday)


async def retry_async(
    func: Callable[..., T],
    *args: Any,
    max_retries: Optional[int] = None,
    **kwargs: Any
) -> T:
    """
    Декоратор для повтора асинхронной функции с экспоненциальной задержкой.

    Args:
        func: Асинхронная функция для выполнения
        *args: Позиционные аргументы функции
        max_retries: Максимальное количество попыток
        **kwargs: Именованные аргументы функции

    Returns:
        Результат выполнения функции

    Raises:
        Exception: Последняя ошибка после всех попыток
    """
    from .config import get_config
    config = get_config()
    retries = max_retries if max_retries is not None else config.max_retries
    delay = config.retry_delay

    last_exception = None

    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                wait_time = delay * (config.retry_exponential_base ** attempt)
                logger.warning(
                    "retry_attempt_failed",
                    function=func.__name__,
                    attempt=attempt + 1,
                    max_retries=retries,
                    wait_time=wait_time,
                    error=str(e)
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    "retry_exhausted",
                    function=func.__name__,
                    max_retries=retries,
                    error=str(e)
                )

    raise last_exception


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