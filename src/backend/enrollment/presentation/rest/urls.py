"""
Enrollment REST API v1.
"""

from django.urls import path, include

urlpatterns = [
    path('enrollments/', include('src.backend.enrollment.presentation.rest.enrollments.urls')),
]
