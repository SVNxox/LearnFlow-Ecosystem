from django.urls import path
from .course_detail import AdminCourseDetailView

urlpatterns = [
    path('courses/<uuid:course_id>/', AdminCourseDetailView.as_view(), name='admin-course-detail'),
]