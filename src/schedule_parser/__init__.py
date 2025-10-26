"""
Schedule Parser - Асинхронный модуль для парсинга расписания учебных групп.

Основные функции:
- parse_group(group_id) - Парсинг расписания одной группы
- parse_groups_batch(group_ids) - Параллельный парсинг нескольких групп

Использование:
    from parser import parse_group, parse_groups_batch, configure_logging

    # Настройка логирования
    configure_logging("INFO")

    # Парсинг одной группы
    result = await parse_group(123)

    # Парсинг нескольких групп
    results = await parse_groups_batch([123, 456, 789])
"""

from .parser import parse_group, parse_groups_batch
from .models import ParseResult, Lesson, WeekType, ChangeType, GroupInfo
from .db import get_database, Database
from .config import Config, get_config
from .utils import configure_logging

__version__ = "1.0.1"

__all__ = [
    # Основные функции парсинга
    "parse_group",
    "parse_groups_batch",

    # Модели данных
    "ParseResult",
    "Lesson",
    "WeekType",
    "ChangeType",
    "GroupInfo",

    # База данных
    "get_database",
    "Database",

    # Конфигурация
    "Config",
    "get_config",

    # Утилиты
    "configure_logging",
]
