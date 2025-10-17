"""
Вспомогательные функции и утилиты.
"""

import asyncio
import logging
import re
from datetime import date, time, datetime, timedelta
from typing import Optional, Callable, TypeVar, Any
from functools import wraps

import structlog
from .config import get_config

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


def parse_time_range(time_str: str) -> tuple[time, time] | None:
    """
    Парсинг временного диапазона из строки.
    
    Args:
        time_str: Строка вида "09:00-10:35"
        
    Returns:
        Кортеж (start_time, end_time) или None при ошибке
    """
    match = re.match(r'(\d{2}):(\d{2})-(\d{2}):(\d{2})', time_str.strip())
    if not match:
        return None
    
    h1, m1, h2, m2 = map(int, match.groups())
    return time(h1, m1), time(h2, m2)


def normalize_text(text: str) -> str:
    """
    Нормализация текста: удаление лишних пробелов и символов.
    
    Args:
        text: Исходный текст
        
    Returns:
        Нормализованный текст
    """
    return ' '.join(text.strip().split())


def parse_lesson_info(raw_text: str) -> dict[str, Optional[str]]:
    """
    Извлечение информации об уроке из сырого текста.

    Формат: "тип.Название ПРЕПОДАВАТЕЛЬ а.АУДИТОРИЯ"
    Примеры:
        "лек.История МИХЕЕВ Б.В. а.15-466"
        "пр.Иностранный язык- 1 п/г ЦЫБИКОВА Л.Б. а.0331"
        "лаб.Основы проект. деят-ти АНГАРХАЕВА Ю.П. а.0107"

    Args:
        raw_text: Сырой текст из HTML

    Returns:
        Словарь с полями: lesson_type, name, teacher, cabinet
    """
    text = normalize_text(raw_text)

    # Пустой урок
    if text == '_' or not text:
        return {
            "lesson_type": None,
            "name": None,
            "teacher": None,
            "cabinet": None,
        }

    result = {
        "lesson_type": None,
        "name": None,
        "teacher": None,
        "cabinet": None,
    }

    # Извлечение типа занятия (лек., пр., лаб.)
    type_match = re.match(r'^(лек|пр|лаб)\.', text)
    if type_match:
        result["lesson_type"] = type_match.group(1)
        text = text[len(type_match.group(0)):].strip()

    # Извлечение аудитории (а.НОМЕР)
    cabinet_match = re.search(r'\s+а\.([^\s]+)', text)
    if cabinet_match:
        result["cabinet"] = cabinet_match.group(1)
        text = text[:cabinet_match.start()] + text[cabinet_match.end():]
        text = text.strip()

    # Теперь разделяем название и преподавателя
    # Преподаватель - это обычно 2-3 слова в конце в формате:
    # ФАМИЛИЯ И.О. или ФАМИЛИЯ И. или просто ФАМИЛИЯ
    # Паттерн: заглавные буквы, возможно с точками и пробелами
    teacher_pattern = r'\s+([А-ЯЁ]+(?:\s+[А-ЯЁ]\.(?:\s*[А-ЯЁ]\.)?)?)$'
    teacher_match = re.search(teacher_pattern, text)

    if teacher_match:
        result["teacher"] = teacher_match.group(1).strip()
        result["name"] = text[:teacher_match.start()].strip()
    else:
        # Если не нашли преподавателя по паттерну, всё идёт в название
        result["name"] = text.strip()

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
