"""
Enrollment API URLs.
"""

from django.urls import path

from .create import CreateEnrollmentView
from .list import ListEnrollmentsView
from .detail import EnrollmentDetailView
from .drop import DropEnrollmentView
from .check_access import CheckAccessView


class EnrollmentListCreateView(CreateEnrollmentView, ListEnrollmentsView):
    """Combined view for GET (list) and POST (create) enrollments."""
    pass


urlpatterns = [
    
    
    path('', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),

    
    path('<str:enrollment_id>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),

    
    path('<str:enrollment_id>/drop/', DropEnrollmentView.as_view(), name='enrollment-drop'),

    
    path('<str:enrollment_id>/check-access/', CheckAccessView.as_view(), name='enrollment-check-access'),
]
