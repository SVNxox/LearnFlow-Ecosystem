"""
tests/learning/test_queries.py

Tests for Learning Domain Queries.
"""
import pytest

pytestmark = pytest.mark.django_db






class TestCourseCatalogQuery:
    def test_get_published_courses(self, course, draft_course):
        from src.backend.learning.application.queries import CourseCatalogQuery

        courses = CourseCatalogQuery.get_published_courses()

        course_ids = [str(c.id) for c in courses]
        assert str(course.id) in course_ids
        assert str(draft_course.id) not in course_ids

    def test_search_courses(self, course):
        from src.backend.learning.application.queries import CourseCatalogQuery

        courses = CourseCatalogQuery.search_courses(query="Test")

        assert courses.count() >= 1
        course_ids = [str(c.id) for c in courses]
        assert str(course.id) in course_ids

    def test_get_all_categories(self, course_category):
        from src.backend.learning.application.queries import CourseCatalogQuery

        categories = CourseCatalogQuery.get_all_categories()

        assert len(categories) >= 1






class TestCourseDetailQuery:
    def test_get_course_detail(self, course, module_factory, lesson_factory):
        from src.backend.learning.application.queries import CourseDetailQuery

        module = module_factory.create(course=course, is_published=True)
        lesson = lesson_factory.create(module=module, is_published=True)

        course_detail = CourseDetailQuery.get_course_detail(
            course_id=str(course.id), user=None
        )

        assert course_detail.title == course.title
        assert len(course_detail.modules) >= 1

    def test_get_course_by_slug(self, course):
        from src.backend.learning.application.queries import CourseDetailQuery

        course_detail = CourseDetailQuery.get_course_by_slug(
            slug=course.slug, user=None
        )

        assert course_detail.title == course.title

    def test_returns_none_for_nonexistent_course(self):
        from src.backend.learning.application.queries import CourseDetailQuery

        course_detail = CourseDetailQuery.get_course_detail(
            course_id="nonexistent", user=None
        )

        assert course_detail is None






class TestLessonDetailQuery:
    def test_get_lesson_detail(self, lesson):
        from src.backend.learning.application.queries import LessonDetailQuery

        lesson_detail = LessonDetailQuery.get_lesson_detail(
            lesson_id=str(lesson.id), user=None
        )

        assert lesson_detail.title == lesson.title

    def test_get_lessons_for_module(self, lesson, module):
        from src.backend.learning.application.queries import LessonDetailQuery

        lessons = LessonDetailQuery.get_lessons_for_module(
            module_id=str(module.id), user=None
        )

        assert lessons.count() >= 1
