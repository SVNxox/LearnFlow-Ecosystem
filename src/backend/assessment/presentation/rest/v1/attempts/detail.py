"""
GET /api/v1/assessment/attempts/{attempt_id}/

Get attempt details with all responses.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.assessment.domain.models import AssessmentAttempt
from src.backend.assessment.application.queries import GetAttemptDetailQuery


class AttemptDetailView(APIView):
    """
    Get full attempt details.

    Shows all items with responses and grading results.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        """
        GET /api/v1/assessment/attempts/{attempt_id}/

        Returns:
        {
            "attempt_id": "uuid",
            "assessment_id": "uuid",
            "assessment_title": "Python Basics Quiz",
            "attempt_number": 1,
            "grading_status": "finalized",
            "started_at": "2026-06-09T16:00:00Z",
            "submitted_at": "2026-06-09T16:45:00Z",
            "expires_at": "2026-06-09T17:30:00Z",
            "is_expired": false,
            "max_score": 100.00,
            "final_score": 85.00,
            "percentage": 85.00,
            "passed": true,
            "passing_percentage": 70.00,
            "items": [
                {
                    "item_id": "uuid",
                    "item_type": "single_choice",
                    "item_title": "What is Python?",
                    "order": 1,
                    "max_points": 10.00,
                    "selected_option_ids": ["uuid"],
                    "is_graded": true,
                    "final_points": 10.00,
                    "is_correct": true
                }
            ],
            "total_items": 10,
            "graded_items": 10
        }
        """
        
        attempt = get_object_or_404(
            AssessmentAttempt,
            id=attempt_id,
            user_id=request.user.id
        )

        query = GetAttemptDetailQuery(attempt_id=attempt_id)
        result = query.execute()

        return Response({
            'attempt_id': str(result.attempt_id),
            'assessment_id': str(result.assessment_id),
            'assessment_title': result.assessment_title,
            'attempt_number': result.attempt_number,
            'grading_status': result.grading_status,
            'started_at': result.started_at.isoformat(),
            'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None,
            'graded_at': result.graded_at.isoformat() if result.graded_at else None,
            'expires_at': result.expires_at.isoformat() if result.expires_at else None,
            'is_expired': result.is_expired,
            'max_score': float(result.max_score),
            'final_score': float(result.final_score) if result.final_score else None,
            'percentage': float(result.percentage) if result.percentage else None,
            'passed': result.passed,
            'passing_percentage': float(result.passing_percentage),
            'items': [
                {
                    'item_id': str(item.item_id),
                    'item_type': item.item_type,
                    'item_title': item.item_title,
                    'order': item.order,
                    'max_points': float(item.max_points),
                    'options': [
                        {
                            'id': str(opt.id),
                            'text': opt.text,
                            'order': opt.order
                        }
                        for opt in item.options
                    ] if item.options else None,
                    'selected_option_ids': [str(oid) for oid in item.selected_option_ids],
                    'text_response': item.text_response,
                    'submitted_code': item.submitted_code,
                    'is_graded': item.is_graded,
                    'auto_points': float(item.auto_points) if item.auto_points else None,
                    'mentor_points': float(item.mentor_points) if item.mentor_points else None,
                    'final_points': float(item.final_points) if item.final_points else None,
                    'is_correct': item.is_correct,
                    'review_comment': item.review_comment,
                }
                for item in result.items
            ],
            'total_items': result.total_items,
            'graded_items': result.graded_items,
            'mentor_note': result.mentor_note,
        })
