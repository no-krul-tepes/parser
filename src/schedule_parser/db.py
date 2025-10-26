"""
Модуль для работы с базой данных PostgreSQL через asyncpg.
"""

import json
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
import structlog

from .models import Lesson, WeekType, ChangeType, GroupInfo
from .config import get_config

logger = structlog.get_logger()


class Database:
    """Класс для работы с базой данных."""
    
    def __init__(self, connection_string: str):
        """
        Инициализация подключения к БД.
        
        Args:
            connection_string: Строка подключения PostgreSQL
        """
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Создание пула подключений к БД."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("database_connected")
    
    async def disconnect(self) -> None:
        """Закрытие пула подключений."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("database_disconnected")
    
    async def get_group_info(self, group_id: int) -> Optional[GroupInfo]:
        """
        Получить информацию о группе.
        
        Args:
            group_id: ID группы
            
        Returns:
            GroupInfo или None, если группа не найдена
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT GroupId, Name, Url, InstitutionId, DepartmentId, Course
                FROM "Group"
                WHERE GroupId = $1 AND IsActive = TRUE
                """,
                group_id
            )
            
            if row:
                return GroupInfo(
                    group_id=row['groupid'],
                    name=row['name'],
                    url=row['url'],
                    institution_id=row['institutionid'],
                    department_id=row['departmentid'],
                    course=row['course']
                )
            return None
    
    async def get_active_groups(self) -> list[int]:
        """
        Получить список ID активных групп с подписанными чатами.
        
        Returns:
            Список group_id
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT g.GroupId
                FROM "Group" g
                INNER JOIN Chat c ON g.GroupId = c.GroupId
                WHERE g.IsActive = TRUE
                """
            )
            return [row['groupid'] for row in rows]

    async def get_existing_lessons(
        self,
        group_id: int,
        week_type: WeekType,
        conn: Optional[asyncpg.Connection] = None
    ) -> list[Lesson]:
        """
        Получить существующие уроки для группы и типа недели.

        Args:
            group_id: ID группы
            week_type: Тип недели
            conn: Опциональное подключение для переиспользования

        Returns:
            Список существующих уроков
        """
        async def _fetch(connection: asyncpg.Connection) -> list[Lesson]:
            rows = await connection.fetch(
                """
                SELECT 
                    LessonId, GroupId, Name, LessonDate, DayOfWeek,
                    LessonNumber, StartTime, EndTime, TeacherName,
                    CabinetNumber, WeekType, lesson_type, Subgroup,
                    RawText, DateAdded, LastUpdated
                FROM Lesson
                WHERE GroupId = $1 AND WeekType = $2
                ORDER BY DayOfWeek, LessonNumber
                """,
                group_id,
                week_type.value
            )
            return [
                Lesson(
                    lesson_id=row['lessonid'],
                    group_id=row['groupid'],
                    name=row['name'],
                    lesson_date=row['lessondate'],
                    day_of_week=row['dayofweek'],
                    lesson_number=row['lessonnumber'],
                    start_time=row['starttime'],
                    end_time=row['endtime'],
                    teacher_name=row['teachername'],
                    cabinet_number=row['cabinetnumber'],
                    week_type=WeekType(row['weektype']),
                    subgroup=row['subgroup'],
                    lesson_type=row['lesson_type'],
                    raw_text=row['rawtext'],
                    date_added=row['dateadded'],
                    last_updated=row['lastupdated']
                )
                for row in rows
            ]

        if conn is not None:
            return await _fetch(conn)

        async with self.pool.acquire() as connection:
            return await _fetch(connection)

    async def insert_lesson(self, lesson: Lesson, conn: Optional[asyncpg.Connection] = None) -> int:
        """
        Вставить новый урок в БД.

        Args:
            lesson: Объект урока
            conn: Опциональное подключение для переиспользования

        Returns:
            ID созданного урока
        """
        async def _execute(connection: asyncpg.Connection) -> int:
            row = await connection.fetchrow(
                """
                INSERT INTO Lesson (
                    GroupId, Name, LessonDate, DayOfWeek, LessonNumber,
                    StartTime, EndTime, TeacherName, CabinetNumber,
                    WeekType, lesson_type, Subgroup, RawText
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING LessonId
                """,
                lesson.group_id,
                lesson.name,
                lesson.lesson_date,
                lesson.day_of_week,
                lesson.lesson_number,
                lesson.start_time,
                lesson.end_time,
                lesson.teacher_name,
                lesson.cabinet_number,
                lesson.week_type.value,
                lesson.lesson_type,
                lesson.subgroup,
                lesson.raw_text
            )
            return row['lessonid']

        if conn is not None:
            return await _execute(conn)

        async with self.pool.acquire() as connection:
            return await _execute(connection)

    async def update_lesson(self, lesson: Lesson, conn: Optional[asyncpg.Connection] = None) -> None:
        """
        Обновить существующий урок.

        Args:
            lesson: Объект урока с заполненным lesson_id
            conn: Опциональное подключение для переиспользования
        """
        async def _execute(connection: asyncpg.Connection) -> None:
            await connection.execute(
                """
                UPDATE Lesson
                SET Name = $2, LessonDate = $3, DayOfWeek = $4,
                    LessonNumber = $5, StartTime = $6, EndTime = $7,
                    TeacherName = $8, CabinetNumber = $9, lesson_type = $10,
                    Subgroup = $11, RawText = $12
                WHERE LessonId = $1
                """,
                lesson.lesson_id,
                lesson.name,
                lesson.lesson_date,
                lesson.day_of_week,
                lesson.lesson_number,
                lesson.start_time,
                lesson.end_time,
                lesson.teacher_name,
                lesson.cabinet_number,
                lesson.lesson_type,
                lesson.subgroup,
                lesson.raw_text
            )

        if conn is not None:
            await _execute(conn)
            return

        async with self.pool.acquire() as connection:
            await _execute(connection)

    async def delete_lesson(self, lesson_id: int, conn: Optional[asyncpg.Connection] = None) -> None:
        """
        Удалить урок из БД.

        Args:
            lesson_id: ID урока
            conn: Опциональное подключение для переиспользования
        """
        async def _execute(connection: asyncpg.Connection) -> None:
            await connection.execute(
                "DELETE FROM Lesson WHERE LessonId = $1",
                lesson_id
            )

        if conn is not None:
            await _execute(conn)
            return

        async with self.pool.acquire() as connection:
            await _execute(connection)

    async def log_schedule_change(
        self,
        lesson_id: int,
        change_type: ChangeType,
        old_data: Optional[dict] = None,
        new_data: Optional[dict] = None,
        conn: Optional[asyncpg.Connection] = None
    ) -> None:
        """
        Записать изменение в журнал.

        Args:
            lesson_id: ID урока
            change_type: Тип изменения
            old_data: Старые данные (для update/delete)
            new_data: Новые данные (для new/update)
            conn: Опциональное подключение для переиспользования
        """
        async def _execute(connection: asyncpg.Connection) -> None:
            await connection.execute(
                """
                INSERT INTO schedule_changes (LessonId, ChangeType, OldData, NewData)
                VALUES ($1, $2, $3, $4)
                """,
                lesson_id,
                change_type.value,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None
            )

        if conn is not None:
            await _execute(conn)
            return

        async with self.pool.acquire() as connection:
            await _execute(connection)
    
    async def ensure_connected(self) -> None:
        """Гарантирует наличие пула подключений."""
        if self.pool is None:
            await self.connect()

    async def fetch(self, query: str, *args) -> list[dict]:
        """Выполнить запрос и получить все строки."""
        await self.ensure_connected()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return rows

    async def fetchrow(self, query: str, *args) -> Optional[dict]:
        """Выполнить запрос и получить одну строку."""
        await self.ensure_connected()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return row

    async def execute(self, query: str, *args) -> str:
        """Выполнить SQL команду."""
        await self.ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    @asynccontextmanager
    async def acquire_connection(self) -> asyncpg.Connection:
        """Контекстный менеджер для переиспользования соединения."""
        await self.ensure_connected()
        assert self.pool is not None
        connection = await self.pool.acquire()
        try:
            yield connection
        finally:
            await self.pool.release(connection)
    
    async def __aenter__(self):
        """Контекстный менеджер: вход."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход."""
        await self.disconnect()


# Глобальный экземпляр для переиспользования
_db_instance: Optional[Database] = None


async def get_database() -> Database:
    """
    Получить глобальный экземпляр базы данных.
    
    Returns:
        Подключенный экземпляр Database
    """
    global _db_instance
    
    if _db_instance is None:
        config = get_config()
        _db_instance = Database(config.database_url)
        await _db_instance.connect()
    
    return _db_instance
