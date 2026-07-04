"""
tests/learning/test_commands.py

Tests for Learning Domain Commands.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import transaction

pytestmark = pytest.mark.django_db






class TestCreateCourseCommand:
    def test_create_course_success(self, staff_user):
        from src.backend.learning.application.commands import CreateCourseCommand, CreateCourseData

        data = CreateCourseData(
            title="Test Course",
            description="Test description",
            supports_online=True,
            language="ru",
        )

        with transaction.atomic():
            course = CreateCourseCommand.execute(data=data, actor=staff_user)

        assert course.title == "Test Course"
        assert course.status == "draft"
        assert course.supports_online is True
        assert course.language == "ru"

    def test_requires_staff_permission(self, active_user):
        from src.backend.learning.application.commands import CreateCourseCommand, CreateCourseData

        data = CreateCourseData(title="Test Course", supports_online=True)

        with pytest.raises(Exception):  
            with transaction.atomic():
                CreateCourseCommand.execute(data=data, actor=active_user)

    def test_title_validation(self, staff_user):
        from src.backend.learning.application.commands import CreateCourseCommand, CreateCourseData

        data = CreateCourseData(title="ab", supports_online=True)  

        with pytest.raises(ValidationError):
            with transaction.atomic():
                CreateCourseCommand.execute(data=data, actor=staff_user)






class TestPublishCourseCommand:
    def test_publish_success(self, staff_user, draft_course):
        from src.backend.learning.application.commands import PublishCourseCommand

        course = PublishCourseCommand.execute(
            course_id=str(draft_course.id), actor=staff_user
        )

        assert course.status == "published"

    def test_publish_requires_published_modules(self, staff_user, draft_course):
        from src.backend.learning.application.commands import PublishCourseCommand

        
        with pytest.raises(ValidationError):
            with transaction.atomic():
                PublishCourseCommand.execute(
                    course_id=str(draft_course.id), actor=staff_user
                )

    def test_unpublish_success(self, staff_user, published_course):
        from src.backend.learning.application.commands import PublishCourseCommand

        course = PublishCourseCommand.unpublish_course(
            course_id=str(published_course.id), actor=staff_user
        )

        assert course.status == "draft"






class TestUpdateModuleCommand:
    def test_update_module_success(self, staff_user, module):
        from src.backend.learning.application.commands import UpdateModuleCommand, UpdateModuleData

        data = UpdateModuleData(title="Updated Title")

        module = UpdateModuleCommand.execute(
            module_id=str(module.id), data=data, actor=staff_user
        )

        assert module.title == "Updated Title"

    def test_publish_module_requires_lessons(self, staff_user, draft_module):
        from src.backend.learning.application.commands import UpdateModuleCommand

        with pytest.raises(ValidationError):
            with transaction.atomic():
                UpdateModuleCommand.publish_module(
                    module_id=str(draft_module.id), actor=staff_user
                )






class TestUpdateLessonCommand:
    def test_update_lesson_success(self, staff_user, lesson):
        from src.backend.learning.application.commands import UpdateLessonCommand, UpdateLessonData

        data = UpdateLessonData(title="Updated Title")

        lesson = UpdateLessonCommand.execute(
            lesson_id=str(lesson.id), data=data, actor=staff_user
        )

        assert lesson.title == "Updated Title"

    def test_publish_lesson_requires_content(self, staff_user, draft_lesson):
        from src.backend.learning.application.commands import UpdateLessonCommand

        with pytest.raises(ValidationError):
            with transaction.atomic():
                UpdateLessonCommand.publish_lesson(
                    lesson_id=str(draft_lesson.id), actor=staff_user
                )
