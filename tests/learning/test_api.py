"""
tests/learning/test_api.py

Full HTTP stack tests via DRF APIClient for Learning Domain endpoints.
"""
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status

pytestmark = pytest.mark.django_db






def get_course_list_url():
    return reverse("learning:course-list")


def get_course_create_url():
    return reverse("learning:course-create")


def get_course_detail_url(course_id):
    return reverse("learning:course-detail", kwargs={"slug": course_id})


def get_course_publish_url(course_id):
    return reverse("learning:course-publish", kwargs={"course_id": course_id})


def get_course_unpublish_url(course_id):
    return reverse("learning:course-unpublish", kwargs={"course_id": course_id})


def get_module_list_url():
    return reverse("learning:module-list")


def get_module_create_url():
    return reverse("learning:module-create")


def get_module_detail_url(module_id):
    return reverse("learning:module-detail", kwargs={"module_id": module_id})


def get_module_publish_url(module_id):
    return reverse("learning:module-publish", kwargs={"module_id": module_id})


def get_module_unpublish_url(module_id):
    return reverse("learning:module-unpublish", kwargs={"module_id": module_id})


def get_module_reorder_url():
    return reverse("learning:module-reorder")


def get_lesson_list_url():
    return reverse("learning:lesson-list")


def get_lesson_create_url():
    return reverse("learning:lesson-create")


def get_lesson_detail_url(lesson_id):
    return reverse("learning:lesson-detail", kwargs={"lesson_id": lesson_id})


def get_lesson_publish_url(lesson_id):
    return reverse("learning:lesson-publish", kwargs={"lesson_id": lesson_id})


def get_lesson_unpublish_url(lesson_id):
    return reverse("learning:lesson-unpublish", kwargs={"lesson_id": lesson_id})


def get_lesson_reorder_url():
    return reverse("learning:lesson-reorder")






class TestCourseListAPI:
    URL = get_course_list_url

    def test_200_on_success(self, api_client, course):
        resp = api_client.get(self.URL())
        assert resp.status_code == status.HTTP_200_OK

    def test_returns_published_courses(self, api_client, course, draft_course):
        resp = api_client.get(self.URL())
        assert resp.status_code == status.HTTP_200_OK
        course_ids = [c["id"] for c in resp.data["results"]]
        assert str(course.id) in course_ids
        assert str(draft_course.id) not in course_ids

    def test_pagination(self, api_client, courses_factory):
        courses_factory.create_batch(25)
        resp = api_client.get(self.URL())
        assert resp.status_code == status.HTTP_200_OK
        assert "count" in resp.data
        assert "total_pages" in resp.data
        assert len(resp.data["results"]) <= 20  


class TestCourseCreateAPI:
    URL = get_course_create_url

    @patch("src.backend.learning.tasks.fan_out_course_published.delay")
    def test_201_on_success(self, mock_task, admin_client):
        payload = {
            "title": "Test Course",
            "description": "A test course",
            "supports_online": True,
            "language": "ru",
        }
        resp = admin_client.post(self.URL(), payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["title"] == "Test Course"
        assert resp.data["status"] == "draft"

    def test_requires_staff_permission(self, api_client, active_user, access_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        payload = {"title": "Test Course", "supports_online": True}
        resp = api_client.post(self.URL(), payload, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestCourseDetailAPI:
    def test_200_on_success(self, api_client, course):
        url = get_course_detail_url(course.slug)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == course.title

    def test_returns_404_for_nonexistent_course(self, api_client):
        url = get_course_detail_url("nonexistent-slug")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestCoursePublishAPI:
    def test_200_on_success(self, authed_client, draft_course_with_lessons):
        url = get_course_publish_url(draft_course_with_lessons.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "published"

    def test_requires_authorization(self, api_client, course):
        url = get_course_publish_url(course.id)
        resp = api_client.post(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestCourseUnpublishAPI:
    def test_200_on_success(self, authed_client, published_course):
        url = get_course_unpublish_url(published_course.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "draft"






class TestModuleListAPI:
    def test_200_on_success(self, api_client, course, module_factory):
        module_factory.create_batch(3, course=course)
        url = get_module_list_url()
        resp = api_client.get(url, {"course_id": str(course.id)})
        assert resp.status_code == status.HTTP_200_OK

    def test_returns_published_modules(self, api_client, course, module_factory):
        published = module_factory.create(course=course, is_published=True)
        draft = module_factory.create(course=course, is_published=False)
        url = get_module_list_url()
        resp = api_client.get(url, {"course_id": str(course.id)})
        assert resp.status_code == status.HTTP_200_OK
        module_ids = [m["id"] for m in resp.data]
        assert str(published.id) in module_ids
        assert str(draft.id) not in module_ids


class TestModuleCreateAPI:
    def test_201_on_success(self, authed_client, course):
        payload = {
            "title": "Test Module",
            "description": "A test module",
            "course_id": str(course.id),
        }
        url = get_module_create_url()
        resp = authed_client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["title"] == "Test Module"
        assert resp.data["is_published"] is False


class TestModuleDetailAPI:
    def test_200_on_success(self, api_client, module):
        url = get_module_detail_url(module.id)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == module.title


class TestModulePublishAPI:
    def test_200_on_success(self, authed_client, draft_module_with_lessons):
        url = get_module_publish_url(draft_module_with_lessons.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_published"] is True


class TestModuleUnpublishAPI:
    def test_200_on_success(self, authed_client, published_module):
        url = get_module_unpublish_url(published_module.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_published"] is False


class TestModuleReorderAPI:
    def test_200_on_success(self, authed_client, course, module_factory):
        modules = module_factory.create_batch(3, course=course)
        ordered_ids = [str(m.id) for m in reversed(modules)]
        payload = {"ordered_ids": ordered_ids}
        url = get_module_reorder_url()
        resp = authed_client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3

    def test_requires_complete_list(self, authed_client, course, module_factory):
        modules = module_factory.create_batch(3, course=course)
        payload = {"ordered_ids": [str(modules[0].id)]}  
        url = get_module_reorder_url()
        resp = authed_client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST






class TestLessonListAPI:
    def test_200_on_success(self, api_client, module, lesson_factory):
        lesson_factory.create_batch(3, module=module)
        url = get_lesson_list_url()
        resp = api_client.get(url, {"module_id": str(module.id)})
        assert resp.status_code == status.HTTP_200_OK


class TestLessonCreateAPI:
    def test_201_on_success(self, authed_client, module):
        payload = {
            "title": "Test Lesson",
            "description": "A test lesson",
            "module_id": str(module.id),
        }
        url = get_lesson_create_url()
        resp = authed_client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["title"] == "Test Lesson"
        assert resp.data["is_published"] is False


class TestLessonDetailAPI:
    def test_200_on_success(self, api_client, lesson):
        url = get_lesson_detail_url(lesson.id)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == lesson.title


class TestLessonPublishAPI:
    def test_200_on_success(self, authed_client, draft_lesson_with_content):
        url = get_lesson_publish_url(draft_lesson_with_content.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_published"] is True


class TestLessonUnpublishAPI:
    def test_200_on_success(self, authed_client, published_lesson):
        url = get_lesson_unpublish_url(published_lesson.id)
        resp = authed_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_published"] is False


class TestLessonReorderAPI:
    def test_200_on_success(self, authed_client, module, lesson_factory):
        lessons = lesson_factory.create_batch(3, module=module)
        ordered_ids = [str(l.id) for l in reversed(lessons)]
        payload = {"ordered_ids": ordered_ids}
        url = get_lesson_reorder_url()
        resp = authed_client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3
