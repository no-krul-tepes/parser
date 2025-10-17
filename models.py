"""
Модели данных для парсера расписания.
"""

from dataclasses import dataclass, field
from datetime import date, time, datetime
from enum import Enum
from typing import Optional


class WeekType(str, Enum):
    """Тип недели (четная/нечетная)."""
    EVEN = "even"
    ODD = "odd"


class ChangeType(str, Enum):
    """Тип изменения в расписании."""
    NEW = "new"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class Lesson:
    """Модель урока."""
    group_id: int
    name: str
    lesson_date: date
    day_of_week: int
    lesson_number: int
    start_time: time
    end_time: time
    week_type: WeekType
    teacher_name: Optional[str] = None
    cabinet_number: Optional[str] = None
    raw_text: Optional[str] = None
    lesson_id: Optional[int] = None
    date_added: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __eq__(self, other) -> bool:
        """Сравнение уроков для определения изменений."""
        if not isinstance(other, Lesson):
            return False
        return (
            self.name == other.name
            and self.teacher_name == other.teacher_name
            and self.cabinet_number == other.cabinet_number
            and self.start_time == other.start_time
            and self.end_time == other.end_time
        )


@dataclass
class ParseResult:
    """Результат парсинга расписания группы."""
    status: bool
    group_id: int
    details: str
    lessons_added: int = 0
    lessons_updated: int = 0
    lessons_deleted: int = 0
    errors: Optional[str] = None
    parsed_at: datetime = field(default_factory=datetime.now)

    @property
    def total_changes(self) -> int:
        """Общее количество изменений."""
        return self.lessons_added + self.lessons_updated + self.lessons_deleted


@dataclass
class GroupInfo:
    """Информация о группе для парсинга."""
    group_id: int
    name: str
    url: str
    institution_id: int
    department_id: int
    course: int
