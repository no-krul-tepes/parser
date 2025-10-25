"""
Модели данных для парсера расписания.
Обновлённая версия с поддержкой подгрупп.
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
    """
    Модель урока.

    Attributes:
        lesson_id: Уникальный идентификатор урока в БД
        group_id: ID группы
        name: Название дисциплины
        lesson_date: Дата урока
        day_of_week: День недели (1-7)
        lesson_number: Номер пары (1-6)
        start_time: Время начала
        end_time: Время окончания
        teacher_name: Имя преподавателя (может содержать несколько через ";")
        cabinet_number: Номер аудитории
        week_type: Тип недели (четная/нечетная)
        subgroup: Номер подгруппы (1, 2 или None для всей группы)
        raw_text: Исходный текст из HTML
        date_added: Дата добавления записи
        last_updated: Дата последнего обновления
    """
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
    subgroup: Optional[int] = None  # Новое поле для подгрупп
    raw_text: Optional[str] = None
    lesson_id: Optional[int] = None
    date_added: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __eq__(self, other) -> bool:
        """
        Сравнение уроков для определения изменений.

        Сравниваем ключевые поля, которые могут меняться в расписании.
        Не сравниваем lesson_id, даты добавления/обновления и raw_text.
        """
        if not isinstance(other, Lesson):
            return False
        return (
            self.name == other.name
            and self.teacher_name == other.teacher_name
            and self.cabinet_number == other.cabinet_number
            and self.start_time == other.start_time
            and self.end_time == other.end_time
            and self.subgroup == other.subgroup  # Учитываем подгруппу
        )

    def __repr__(self) -> str:
        """Строковое представление урока для отладки."""
        subgroup_str = f" (п/г {self.subgroup})" if self.subgroup else ""
        return (
            f"Lesson({self.name}{subgroup_str}, "
            f"day={self.day_of_week}, "
            f"number={self.lesson_number}, "
            f"teacher={self.teacher_name}, "
            f"cabinet={self.cabinet_number})"
        )


@dataclass
class ParseResult:
    """
    Результат парсинга расписания группы.

    Attributes:
        status: Успешность парсинга
        group_id: ID группы
        details: Детальное описание результата
        lessons_added: Количество добавленных уроков
        lessons_updated: Количество обновлённых уроков
        lessons_deleted: Количество удалённых уроков
        errors: Описание ошибок (если были)
        parsed_at: Время парсинга
    """
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

    @property
    def is_successful(self) -> bool:
        """Проверка успешности парсинга."""
        return self.status and self.errors is None

    def __repr__(self) -> str:
        """Строковое представление результата."""
        status_str = "✓" if self.status else "✗"
        changes_str = f"+{self.lessons_added} ~{self.lessons_updated} -{self.lessons_deleted}"
        return (
            f"ParseResult({status_str} group_id={self.group_id}, "
            f"changes={changes_str}, errors={self.errors})"
        )


@dataclass
class GroupInfo:
    """
    Информация о группе для парсинга.

    Attributes:
        group_id: ID группы
        name: Название группы
        url: URL страницы с расписанием
        institution_id: ID учебного заведения
        department_id: ID кафедры
        course: Курс обучения
    """
    group_id: int
    name: str
    url: str
    institution_id: int
    department_id: int
    course: int

    def __repr__(self) -> str:
        """Строковое представление информации о группе."""
        return f"GroupInfo(id={self.group_id}, name={self.name}, course={self.course})"