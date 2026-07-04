"""
Progress REST API v1 URLs

Endpoints:
- GET /api/v1/progress/me/ — dashboard
- GET /api/v1/progress/courses/{enrollment_id}/ — course detail
- GET /api/v1/progress/courses/{enrollment_id}/next/ — next action
- POST /api/v1/progress/lessons/{lesson_id}/content/{content_id}/view/ — record view
"""
from django.urls import path

from .progress.dashboard import MyProgressDashboardView
from .progress.course_detail import CourseProgressDetailView
from .progress.next_action import NextActionView
from .lessons.record_view import RecordContentViewView

app_name = 'progress'

urlpatterns = [
    
    path('me/', MyProgressDashboardView.as_view(), name='my-dashboard'),
    path(
        'courses/<uuid:enrollment_id>/',
        CourseProgressDetailView.as_view(),
        name='course-detail'
    ),
    path(
        'courses/<uuid:enrollment_id>/next/',
        NextActionView.as_view(),
        name='next-action'
    ),

    
    path(
        'lessons/<uuid:lesson_id>/content/<uuid:content_id>/view/',
        RecordContentViewView.as_view(),
        name='record-view'
    ),
]
