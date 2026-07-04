"""
GET /api/v1/assessment/assessments/{assessment_id}/attempts/

Get all attempts for current student on an assessment.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.backend.assessment.application.queries import GetStudentAttemptsQuery


class StudentAttemptsListView(APIView):
    """
    List all attempts for student on an assessment.

    Shows attempt history and retry availability.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        """
        GET /api/v1/assessment/assessments/{assessment_id}/attempts/

        Returns:
        {
            "assessment_id": "uuid",
            "assessment_title": "Python Basics Quiz",
            "attempts": [
                {
                    "attempt_id": "uuid",
                    "attempt_number": 2,
                    "grading_status": "finalized",
                    "started_at": "2026-06-09T15:00:00Z",
                    "final_score": 85.00,
                    "percentage": 85.00,
                    "passed": true
                },
                {
                    "attempt_id": "uuid",
                    "attempt_number": 1,
                    "grading_status": "finalized",
                    "started_at": "2026-06-09T14:00:00Z",
                    "final_score": 65.00,
                    "percentage": 65.00,
                    "passed": false
                }
            ],
            "total_attempts": 2,
            "max_attempts": 3,
            "can_retry": true,
            "best_score": 85.00,
            "best_percentage": 85.00
        }
        """
        query = GetStudentAttemptsQuery(
            user_id=request.user.id,
            assessment_id=assessment_id
        )
        result = query.execute()

        return Response({
            'assessment_id': str(result.assessment_id),
            'assessment_title': result.assessment_title,
            'attempts': [
                {
                    'attempt_id': str(attempt.attempt_id),
                    'attempt_number': attempt.attempt_number,
                    'grading_status': attempt.grading_status,
                    'started_at': attempt.started_at.isoformat(),
                    'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                    'final_score': float(attempt.final_score) if attempt.final_score else None,
                    'percentage': float(attempt.percentage) if attempt.percentage else None,
                    'passed': attempt.passed,
                    'is_expired': attempt.is_expired,
                }
                for attempt in result.attempts
            ],
            'total_attempts': result.total_attempts,
            'max_attempts': result.max_attempts,
            'can_retry': result.can_retry,
            'best_score': float(result.best_score) if result.best_score else None,
            'best_percentage': float(result.best_percentage) if result.best_percentage else None,
        })
