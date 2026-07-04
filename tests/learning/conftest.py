"""
tests/learning/conftest.py

Fixtures for Learning Domain tests.
"""
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def course_factory():
    """Factory for creating courses."""
    from src.backend.learning.domain.models import Course, CourseCategory
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class CourseFactory:
        def create(self, **kwargs):
            defaults = {
                "title": "Test Course",
                "description": "A test course",
                "supports_online": True,
                "language": "ru",
                "status": "draft",
            }
            defaults.update(kwargs)
            return Course.objects.create(**defaults)

        def create_batch(self, count, **kwargs):
            return [self.create(**kwargs) for _ in range(count)]

    return CourseFactory()


@pytest.fixture
def course(course_factory):
    """A single published course."""
    return course_factory.create(status="published", is_sequential=True)


@pytest.fixture
def draft_course(course_factory):
    """A draft course."""
    return course_factory.create(status="draft")


@pytest.fixture
def draft_course_with_lessons(course_factory, module_factory, lesson_factory, staff_user):
    """A draft course with published module and lesson."""
    course = course_factory.create(status="draft")
    module = module_factory.create(course=course, is_published=True)
    lesson = lesson_factory.create(module=module, is_published=True)
    return course


@pytest.fixture
def published_course(course_factory, module_factory, lesson_factory, staff_user):
    """A published course."""
    course = course_factory.create(status="published")
    module = module_factory.create(course=course, is_published=True)
    lesson = lesson_factory.create(module=module, is_published=True)
    return course


@pytest.fixture
def courses_factory():
    """Factory for creating multiple courses."""
    from src.backend.learning.domain.models import Course

    class CoursesFactory:
        def create_batch(self, count, **kwargs):
            return [Course.objects.create(**kwargs) for _ in range(count)]

    return CoursesFactory()


@pytest.fixture
def module_factory():
    """Factory for creating modules."""
    from src.backend.learning.domain.models import Module

    class ModuleFactory:
        def create(self, **kwargs):
            defaults = {
                "title": "Test Module",
                "order": 1,
                "is_published": False,
            }
            defaults.update(kwargs)
            return Module.objects.create(**defaults)

        def create_batch(self, count, **kwargs):
            return [self.create(**kwargs) for _ in range(count)]

    return ModuleFactory()


@pytest.fixture
def module(module_factory, course):
    """A single module."""
    return module_factory.create(course=course, is_published=False)


@pytest.fixture
def draft_module(module_factory, course):
    """A draft module."""
    return module_factory.create(course=course, is_published=False)


@pytest.fixture
def draft_module_with_lessons(module_factory, course, lesson_factory, staff_user):
    """A draft module with published lessons."""
    module = module_factory.create(course=course, is_published=False)
    lesson = lesson_factory.create(module=module, is_published=True)
    return module


@pytest.fixture
def published_module(module_factory, course, lesson_factory):
    """A published module."""
    module = module_factory.create(course=course, is_published=True)
    lesson = lesson_factory.create(module=module, is_published=True)
    return module


@pytest.fixture
def lesson_factory():
    """Factory for creating lessons."""
    from src.backend.learning.domain.models import Lesson, LessonContent

    class LessonFactory:
        def create(self, **kwargs):
            defaults = {
                "title": "Test Lesson",
                "description": "A test lesson",
                "order": 1,
                "is_published": False,
                "is_free_preview": False,
            }
            defaults.update(kwargs)
            lesson = Lesson.objects.create(**defaults)

            
            if not kwargs.get("has_content", False):
                LessonContent.objects.create(
                    lesson=lesson,
                    content_type="text",
                    title="Introduction",
                    body="<p>Lesson content</p>",
                    order=1,
                )

            return lesson

        def create_batch(self, count, **kwargs):
            return [self.create(**kwargs) for _ in range(count)]

    return LessonFactory()


@pytest.fixture
def lesson(lesson_factory, module):
    """A single lesson."""
    return lesson_factory.create(module=module, is_published=False)


@pytest.fixture
def draft_lesson(lesson_factory, module):
    """A draft lesson."""
    return lesson_factory.create(module=module, is_published=False)


@pytest.fixture
def draft_lesson_with_content(lesson_factory, module):
    """A draft lesson with content."""
    return lesson_factory.create(module=module, is_published=False, has_content=True)


@pytest.fixture
def published_lesson(lesson_factory, module):
    """A published lesson."""
    return lesson_factory.create(module=module, is_published=True)
