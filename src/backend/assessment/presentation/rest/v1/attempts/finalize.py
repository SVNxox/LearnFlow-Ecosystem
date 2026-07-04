"""
POST /api/v1/assessment/attempts/{attempt_id}/finalize/

Finalize assessment attempt after all responses submitted.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.assessment.domain.models import AssessmentAttempt
from src.backend.assessment.application.commands import FinalizeAttemptCommand


class FinalizeAttemptView(APIView):
    """
    Finalize assessment attempt.

    Student submits all responses and finalizes the attempt.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        """
        POST /api/v1/assessment/attempts/{attempt_id}/finalize/

        Returns:
        {
            "attempt_id": "uuid",
            "submitted_at": "2026-06-09T16:45:00Z",
            "grading_status": "auto_graded",
            "final_score": 85.00,
            "percentage": 85.00,
            "passed": true
        }
        """
        
        attempt = get_object_or_404(
            AssessmentAttempt,
            id=attempt_id,
            user_id=request.user.id
        )

        try:
            command = FinalizeAttemptCommand(attempt_id=attempt_id)
            attempt = command.execute()

            return Response({
                'attempt_id': str(attempt.id),
                'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                'grading_status': attempt.grading_status,
                'final_score': float(attempt.final_score) if attempt.final_score else None,
                'percentage': float(attempt.percentage) if attempt.percentage else None,
                'passed': attempt.passed,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
