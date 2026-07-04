"""
tests/learning/test_commands_unit.py

Unit tests for Learning Domain Commands (no DB).
"""
import pytest


class TestCreateCourseData:
    """Test CreateCourseData DTO."""
    def test_dataclass_fields(self):
        from src.backend.learning.application.commands.create_course import CreateCourseData

        data = CreateCourseData(
            title="Test Course",
            description="Test description",
            supports_online=True,
            language="ru",
        )

        assert data.title == "Test Course"
        assert data.description == "Test description"
        assert data.supports_online is True
        assert data.language == "ru"


class TestUpdateModuleData:
    """Test UpdateModuleData DTO."""
    def test_dataclass_fields(self):
        from src.backend.learning.application.commands.update_module import UpdateModuleData

        data = UpdateModuleData(
            title="Updated Title",
            description="Updated description",
            estimated_hours=10,
        )

        assert data.title == "Updated Title"
        assert data.description == "Updated description"
        assert data.estimated_hours == 10


class TestUpdateLessonData:
    """Test UpdateLessonData DTO."""
    def test_dataclass_fields(self):
        from src.backend.learning.application.commands.update_lesson import UpdateLessonData

        data = UpdateLessonData(
            title="Updated Title",
            description="Updated description",
            estimated_minutes=30,
            is_free_preview=True,
        )

        assert data.title == "Updated Title"
        assert data.description == "Updated description"
        assert data.estimated_minutes == 30
        assert data.is_free_preview is True


class TestCommandStructure:
    """Test command structure and methods."""
    def test_create_course_command_exists(self):
        from src.backend.learning.application.commands import CreateCourseCommand

        assert hasattr(CreateCourseCommand, "execute")

    def test_publish_course_command_exists(self):
        from src.backend.learning.application.commands import PublishCourseCommand

        assert hasattr(PublishCourseCommand, "execute")
        assert hasattr(PublishCourseCommand, "unpublish_course")

    def test_update_module_command_exists(self):
        from src.backend.learning.application.commands import UpdateModuleCommand

        assert hasattr(UpdateModuleCommand, "execute")
        assert hasattr(UpdateModuleCommand, "publish_module")
        assert hasattr(UpdateModuleCommand, "unpublish_module")
        assert hasattr(UpdateModuleCommand, "reorder_modules")
        assert hasattr(UpdateModuleCommand, "delete_module")

    def test_update_lesson_command_exists(self):
        from src.backend.learning.application.commands import UpdateLessonCommand

        assert hasattr(UpdateLessonCommand, "execute")
        assert hasattr(UpdateLessonCommand, "publish_lesson")
        assert hasattr(UpdateLessonCommand, "unpublish_lesson")
        assert hasattr(UpdateLessonCommand, "reorder_lessons")
        assert hasattr(UpdateLessonCommand, "delete_lesson")


class TestQueryStructure:
    """Test query structure."""
    def test_course_catalog_query_exists(self):
        from src.backend.learning.application.queries import CourseCatalogQuery

        assert hasattr(CourseCatalogQuery, "get_published_courses")
        assert hasattr(CourseCatalogQuery, "get_course_card")
        assert hasattr(CourseCatalogQuery, "get_all_categories")
        assert hasattr(CourseCatalogQuery, "search_courses")

    def test_course_detail_query_exists(self):
        from src.backend.learning.application.queries import CourseDetailQuery

        assert hasattr(CourseDetailQuery, "get_course_detail")
        assert hasattr(CourseDetailQuery, "get_course_by_slug")
        assert hasattr(CourseDetailQuery, "get_course_for_author")

    def test_lesson_detail_query_exists(self):
        from src.backend.learning.application.queries import LessonDetailQuery

        assert hasattr(LessonDetailQuery, "get_lesson_detail")
        assert hasattr(LessonDetailQuery, "get_lessons_for_module")


class TestEventStructure:
    """Test event structure."""
    def test_events_module_exists(self):
        from src.backend.learning.domain import events

        
        assert events is not None
