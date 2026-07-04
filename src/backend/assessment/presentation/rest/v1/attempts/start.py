"""
POST /api/v1/assessment/attempts/

Start a new assessment attempt.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.backend.assessment.application.commands import StartAttemptCommand


class StartAttemptView(APIView):
    """
    Start new assessment attempt.

    Student starts taking an assessment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST /api/v1/assessment/attempts/

        Body:
        {
            "enrollment_id": "uuid",
            "assessment_id": "uuid"
        }

        Returns:
        {
            "attempt_id": "uuid",
            "attempt_number": 1,
            "started_at": "2026-06-09T16:00:00Z",
            "expires_at": "2026-06-09T17:30:00Z",
            "max_score": 100.00,
            "total_items": 10
        }
        """
        enrollment_id = request.data.get('enrollment_id')
        assessment_id = request.data.get('assessment_id')

        if not enrollment_id or not assessment_id:
            return Response(
                {'error': 'enrollment_id and assessment_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            command = StartAttemptCommand(
                enrollment_id=enrollment_id,
                assessment_id=assessment_id,
                user_id=request.user.id
            )
            attempt = command.execute()

            return Response({
                'attempt_id': str(attempt.id),
                'attempt_number': attempt.attempt_number,
                'started_at': attempt.started_at.isoformat(),
                'expires_at': attempt.expires_at.isoformat() if attempt.expires_at else None,
                'max_score': float(attempt.max_score),
                'total_items': attempt.assessment.items.count(),
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
