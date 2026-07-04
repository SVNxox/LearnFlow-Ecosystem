"""
Submissions Domain — REST API v1 URLs
"""
from django.urls import path


try:
    from src.backend.submissions.presentation.rest.assignments.create import CreateAssignmentView
    from src.backend.submissions.presentation.rest.assignments.detail import AssignmentDetailView
    from src.backend.submissions.presentation.rest.v1.assignments.by_lesson import AssignmentByLessonView
    from src.backend.submissions.presentation.rest.submissions.create import CreateSubmissionView
    from src.backend.submissions.presentation.rest.submissions.detail import SubmissionDetailView
    from src.backend.submissions.presentation.rest.submissions.my_submissions import MySubmissionsView
    from src.backend.submissions.presentation.rest.submissions.submit_revision import SubmitRevisionView
    from src.backend.submissions.presentation.rest.reviews.submit_review import SubmitReviewView
    from src.backend.submissions.presentation.rest.reviews.pending_reviews import PendingReviewsView
    from src.backend.submissions.presentation.rest.v1.uploads.presigned_url import GeneratePresignedUploadURLView
    from src.backend.submissions.presentation.rest.v1.uploads.download_url import GeneratePresignedDownloadURLView
    from .all_submissions import AllSubmissionsView, AllSubmissionDetailView
    from .homework_info import HomeworkInfoView
except ImportError as e:
    print(f"❌ Import error: {e}")
    raise

app_name = 'submissions'

urlpatterns = [
    
    path('assignments/', CreateAssignmentView.as_view(), name='assignment-create'),
    path('assignments/<uuid:assignment_id>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/by-lesson/<uuid:lesson_id>/', AssignmentByLessonView.as_view(), name='assignment-by-lesson'),

    
    path('submissions/', CreateSubmissionView.as_view(), name='submission-create'),
    path('submissions/<uuid:submission_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('submissions/my/', MySubmissionsView.as_view(), name='my-submissions'),
    path('submissions/<uuid:submission_id>/revisions/', SubmitRevisionView.as_view(), name='submit-revision'),

    
    path('reviews/', SubmitReviewView.as_view(), name='submit-review'),
    path('reviews/pending/', PendingReviewsView.as_view(), name='pending-reviews'),

    
    path('uploads/presigned-url/', GeneratePresignedUploadURLView.as_view(), name='presigned-upload-url'),
    path('uploads/download-url/<uuid:file_id>/', GeneratePresignedDownloadURLView.as_view(), name='presigned-download-url'),

    
    path("homework/<str:homework_id>/", HomeworkInfoView.as_view(), name="homework-info"),

    
    path('all/', AllSubmissionsView.as_view(), name='all-submissions'),
    path('all/<uuid:submission_id>/', AllSubmissionDetailView.as_view(), name='all-submission-detail'),
]