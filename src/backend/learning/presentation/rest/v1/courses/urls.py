"""
Course REST API URLs.

Routes:
- GET    /api/learning/              - list learning
- POST   /api/learning/              - create course (staff)
- GET    /api/learning/{slug}/       - course detail
- POST   /api/learning/{id}/publish/ - publish course (staff/author)
- POST   /api/learning/{id}/unpublish/ - unpublish course (staff/author)
"""

from django.urls import path

from .admin_detail import CourseAdminDetailView
from .create import CourseCreateView
from .detail import CourseDetailView
from .list import CourseListView
from .publish import CoursePublishView, CourseUnpublishView
from .thumbnail_upload_url import CourseThumbnailUploadUrlView, CourseThumbnailUrlView

urlpatterns = [
    
    path("", CourseListView.as_view(), name="course-list"),
    path("create/", CourseCreateView.as_view(), name="course-create"),

    path('thumbnail/upload-url/', CourseThumbnailUploadUrlView.as_view(), name='course-thumbnail-upload-url'),
    path('thumbnail/url/', CourseThumbnailUrlView.as_view(), name='course-thumbnail-url'),

    path("admin/courses/<str:course_id>/", CourseAdminDetailView.as_view(), name="course-admin-detail"),

    
    path("<str:course_id>/publish/", CoursePublishView.as_view(), name="course-publish"),
    path("<str:course_id>/unpublish/", CourseUnpublishView.as_view(), name="course-unpublish"),

    
    path("<str:slug>/", CourseDetailView.as_view(), name="course-detail"),
]
