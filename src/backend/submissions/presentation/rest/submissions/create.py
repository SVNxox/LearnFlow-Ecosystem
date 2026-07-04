"""
Create Submission API View

POST /api/v1/submissions/ - Create submission with first revision
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from src.backend.submissions.domain.models import (
    Assignment, Submission, SubmissionRevision
)
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.submissions.presentation.rest.submissions.serializers import (
    CreateSubmissionSerializer
)

logger = logging.getLogger(__name__)


class CreateSubmissionView(APIView):
    """
    Create new submission with first revision.

    POST /api/v1/submissions/

    Permissions: IsAuthenticated (Student)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment_id = serializer.validated_data['assignment_id']
        enrollment_id = serializer.validated_data['enrollment_id']
        submission_type = serializer.validated_data.get('submission_type', 'text_answer')
        payload = serializer.validated_data.get('payload', {})
        notes = serializer.validated_data.get('notes', '')

        
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        
        try:
            enrollment = CourseEnrollment.objects.get(
                id=enrollment_id,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return Response(
                {"detail": "Enrollment not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )

        
        if str(enrollment.user_id) != str(request.user.id):
            return Response(
                {"detail": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            enrollment_id=enrollment.id,
            defaults={
                'student_id': request.user.id,
                'status': 'submitted',
                'first_submitted_at': timezone.now(),
            }
        )

        if not created:
            submission.status = 'submitted'

        submission.last_submitted_at = timezone.now()
        submission.current_revision_number += 1
        submission.save()

        
        revision = SubmissionRevision.objects.create(
            submission=submission,
            revision_number=submission.current_revision_number,
            submission_type=submission_type,
            payload=payload,
            notes=notes,
        )

        logger.info(
            f"Submission created: {submission.id} by student {request.user.id} "
            f"for assignment {assignment.id} (revision {revision.revision_number})"
        )

        return Response({
            "id": str(submission.id),
            "status": submission.status,
            "revision_id": str(revision.id),
            "revision_number": revision.revision_number,
            "created_at": submission.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)