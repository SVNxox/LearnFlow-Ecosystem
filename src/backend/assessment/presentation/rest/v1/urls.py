"""
Assessment REST API v1 URLs

Endpoints:
- POST /api/v1/assessment/attempts/ — start attempt
- GET /api/v1/assessment/attempts/{id}/ — attempt detail
- POST /api/v1/assessment/attempts/{id}/responses/ — submit response
- POST /api/v1/assessment/attempts/{id}/finalize/ — finalize attempt
- GET /api/v1/assessment/assessments/{id}/attempts/ — list student attempts
- GET /api/v1/assessment/reviews/pending/ — pending reviews (mentor)
- POST /api/v1/assessment/reviews/{id}/ — submit review (mentor)
"""
from django.urls import path

from .attempts.start import StartAttemptView
from .attempts.detail import AttemptDetailView
from .attempts.submit_response import SubmitResponseView
from .attempts.finalize import FinalizeAttemptView
from .attempts.list import StudentAttemptsListView
from .reviews.pending import PendingReviewsListView
from .reviews.submit import SubmitReviewView
from .student_views import (
    StudentAssessmentListView,
    StudentAssessmentDetailView,
    StartAssessmentAttemptView,
    SubmitAssessmentResponseView,
    SubmitAssessmentAttemptView,
)

app_name = 'assessment'


urlpatterns = [
    
    path('attempts/', StartAttemptView.as_view(), name='start-attempt'),
    path('attempts/<uuid:attempt_id>/', AttemptDetailView.as_view(), name='attempt-detail'),
    path('attempts/<uuid:attempt_id>/responses/', SubmitResponseView.as_view(), name='submit-response'),
    path('attempts/<uuid:attempt_id>/finalize/', FinalizeAttemptView.as_view(), name='finalize-attempt'),

    
    path('assessments/<uuid:assessment_id>/attempts/', StudentAttemptsListView.as_view(), name='student-attempts'),

    
    path('reviews/pending/', PendingReviewsListView.as_view(), name='pending-reviews'),
    path('reviews/<uuid:response_id>/', SubmitReviewView.as_view(), name='submit-review'),

    
    path('student/assessments/', StudentAssessmentListView.as_view(), name='student-assessment-list'),
    path('student/assessments/<uuid:assessment_id>/', StudentAssessmentDetailView.as_view(),
         name='student-assessment-detail'),
    path('student/assessments/<uuid:assessment_id>/start/', StartAssessmentAttemptView.as_view(),
         name='start-assessment-attempt'),
    path('student/attempts/<uuid:attempt_id>/responses/', SubmitAssessmentResponseView.as_view(),
         name='submit-assessment-response'),
    path('student/attempts/<uuid:attempt_id>/submit/', SubmitAssessmentAttemptView.as_view(),
         name='submit-assessment-attempt'),
]
