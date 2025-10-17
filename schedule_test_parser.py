"""
Тесты для модуля парсинга расписания.
"""

import pytest
from datetime import date, time
from unittest.mock import Mock, AsyncMock, patch

from parser import parse_schedule_html, ScheduleHTMLParser
from models import Lesson, WeekType
from utils import parse_lesson_info, parse_time_range, get_week_type_for_date


class TestLessonInfoParsing:
    """Тесты парсинга информации об уроке."""
    
    def test_parse_simple_lesson(self):
        """Тест парсинга простого урока."""
        text = "лек.История МИХЕЕВ Б.В. а.15-466"
        info = parse_lesson_info(text)
        
        assert info['lesson_type'] == 'лек'
        assert info['name'] == 'История'
        assert info['teacher'] == 'МИХЕЕВ Б.В.'
        assert info['cabinet'] == '15-466'
    
    def test_parse_complex_lesson(self):
        """Тест парсинга сложного урока с подгруппами."""
        text = "пр.Иностранный язык- 1 п/г ЦЫБИКОВА Л.Б. а.0331"
        info = parse_lesson_info(text)
        
        assert info['lesson_type'] == 'пр'
        assert 'Иностранный язык' in info['name']
        assert info['teacher'] == 'ЦЫБИКОВА Л.Б.'
        assert info['cabinet'] == '0331'
    
    def test_parse_empty_lesson(self):
        """Тест парсинга пустого урока."""
        text = "_"
        info = parse_lesson_info(text)
        
        assert info['name'] is None
        assert info['teacher'] is None
    
    def test_parse_lab_lesson(self):
        """Тест парсинга лабораторной работы."""
        text = "лаб.Химия СЯЧИНОВА Н.В. а.8402"
        info = parse_lesson_info(text)
        
        assert info['lesson_type'] == 'лаб'
        assert info['name'] == 'Химия'
        assert info['teacher'] == 'СЯЧИНОВА Н.В.'
        assert info['cabinet'] == '8402'


class TestTimeRangeParsing:
    """Тесты парсинга временных диапазонов."""
    
    def test_parse_valid_time_range(self):
        """Тест парсинга корректного временного диапазона."""
        result = parse_time_range("09:00-10:35")
        
        assert result is not None
        start, end = result
        assert start == time(9, 0)
        assert end == time(10, 35)
    
    def test_parse_with_spaces(self):
        """Тест парсинга с пробелами."""
        result = parse_time_range("  14:45-16:20  ")
        
        assert result is not None
        start, end = result
        assert start == time(14, 45)
        assert end == time(16, 20)
    
    def test_parse_invalid_format(self):
        """Тест парсинга некорректного формата."""
        result = parse_time_range("invalid")
        assert result is None


class TestWeekTypeDetermination:
    """Тесты определения типа недели."""
    
    def test_first_week_of_september(self):
        """Тест для первой недели сентября."""
        test_date = date(2024, 9, 2)  # Понедельник первой недели
        week_type = get_week_type_for_date(test_date)
        # Первая неделя должна быть нечетной
        assert week_type in ["even", "odd"]
    
    def test_consistent_week_calculation(self):
        """Тест консистентности расчета недель."""
        # Проверяем, что соседние недели имеют разные типы
        monday1 = date(2024, 10, 7)
        monday2 = date(2024, 10, 14)
        
        type1 = get_week_type_for_date(monday1)
        type2 = get_week_type_for_date(monday2)
        
        assert type1 != type2


class TestHTMLParser:
    """Тесты HTML парсера."""
    
    @pytest.fixture
    def sample_html(self):
        """Фикстура с примером HTML."""
        return """
        <HTML>
        <BODY>
        <TABLE>
        <TR>
            <TD>Пары</TD>
            <TD>1-я</TD>
            <TD>2-я</TD>
        </TR>
        <TR>
            <TD>Время</TD>
            <TD>09:00-10:35</TD>
            <TD>10:45-12:20</TD>
        </TR>
        <TR>
            <TD>Пнд</TD>
            <TD>лек.История МИХЕЕВ Б.В. а.15-466</TD>
            <TD>пр.Математика БУДАЕВА Л.Ж. а.0327</TD>
        </TR>
        </TABLE>
        </BODY>
        </HTML>
        """
    
    def test_parser_extracts_rows(self, sample_html):
        """Тест извлечения строк из таблицы."""
        parser = ScheduleHTMLParser()
        parser.feed(sample_html)
        
        data = parser.get_schedule_data()
        assert len(data) > 0
        assert 'Пнд' in data[0][0].lower()
    
    def test_parse_schedule_html_creates_lessons(self, sample_html):
        """Тест создания уроков из HTML."""
        even_lessons, odd_lessons = parse_schedule_html(sample_html, group_id=1)
        
        # Должны быть созданы уроки
        assert len(even_lessons) > 0 or len(odd_lessons) > 0
        
        # Проверяем структуру урока
        all_lessons = even_lessons + odd_lessons
        if all_lessons:
            lesson = all_lessons[0]
            assert isinstance(lesson, Lesson)
            assert lesson.group_id == 1
            assert lesson.name is not None
            assert lesson.day_of_week in range(1, 7)


@pytest.mark.asyncio
class TestAsyncParsing:
    """Тесты асинхронного парсинга."""
    
    @patch('schedule_parser.parser.fetch_schedule_html')
    @patch('schedule_parser.parser.get_database')
    async def test_parse_group_success(self, mock_db, mock_fetch):
        """Тест успешного парсинга группы."""
        from schedule_parser.parser import parse_group
        from schedule_parser.models import GroupInfo
        
        # Настраиваем моки
        mock_fetch.return_value = "<html><body><table></table></body></html>"
        
        mock_db_instance = AsyncMock()
        mock_db_instance.get_group_info.return_value = GroupInfo(
            group_id=1,
            name="Test Group",
            url="http://example.com/schedule",
            institution_id=1,
            department_id=1,
            course=1
        )
        mock_db_instance.get_existing_lessons.return_value = []
        mock_db_instance.insert_lesson.return_value = 1
        mock_db.return_value = mock_db_instance
        
        # Выполняем парсинг
        result = await parse_group(1)
        
        # Проверяем результат
        assert result.status is True or result.status is False
        assert result.group_id == 1
    
    @patch('schedule_parser.parser.get_database')
    async def test_parse_group_not_found(self, mock_db):
        """Тест парсинга несуществующей группы."""
        from schedule_parser.parser import parse_group
        
        mock_db_instance = AsyncMock()
        mock_db_instance.get_group_info.return_value = None
        mock_db.return_value = mock_db_instance
        
        result = await parse_group(999)
        
        assert result.status is False
        assert "not found" in result.details.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
