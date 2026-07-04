"""
Mentorship REST API v1 URLs
"""

from django.urls import path

from src.backend.mentorship.presentation.rest.v1.attendance.mark import MarkAttendanceView
from src.backend.mentorship.presentation.rest.v1.attendance.bulk_mark import BulkMarkAttendanceView
from src.backend.mentorship.presentation.rest.v1.sessions.detail import SessionDetailView
from src.backend.mentorship.presentation.rest.v1.sessions.list import MyGroupSessionsListView

app_name = 'mentorship'

urlpatterns = [
    
    path('sessions/<str:session_id>/attendance/', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('sessions/<str:session_id>/attendance/bulk/', BulkMarkAttendanceView.as_view(), name='bulk-mark-attendance'),

    
    path('sessions/<str:session_id>/', SessionDetailView.as_view(), name='session-detail'),
    path('groups/<str:group_id>/sessions/', MyGroupSessionsListView.as_view(), name='group-sessions'),
]
