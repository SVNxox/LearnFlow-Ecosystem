"""
GET /api/v1/assessment/reviews/pending/

Get list of responses waiting for mentor review.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.backend.assessment.application.queries import GetPendingReviewsQuery


class PendingReviewsListView(APIView):
    """
    List responses waiting for mentor review.

    Mentors use this to see their work queue.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/v1/assessment/reviews/pending/

        Returns:
        {
            "items": [
                {
                    "response_id": "uuid",
                    "attempt_id": "uuid",
                    "assessment_title": "Python Basics Quiz",
                    "user_id": "uuid",
                    "item_type": "text_answer",
                    "item_title": "Explain list comprehension",
                    "max_points": 10.00,
                    "text_response": "Student's answer...",
                    "submitted_at": "2026-06-09T16:00:00Z"
                }
            ],
            "total_count": 15
        }
        """
        
        query = GetPendingReviewsQuery(
            mentor_id=request.user.id,
            limit=100
        )
        result = query.execute()

        return Response({
            'items': [
                {
                    'response_id': str(item.response_id),
                    'attempt_id': str(item.attempt_id),
                    'assessment_id': str(item.assessment_id),
                    'assessment_title': item.assessment_title,
                    'user_id': str(item.user_id),
                    'item_type': item.item_type,
                    'item_title': item.item_title,
                    'max_points': item.max_points,
                    'text_response': item.text_response,
                    'submitted_code': item.submitted_code,
                    'coding_language': item.coding_language,
                    'submitted_at': item.submitted_at.isoformat() if item.submitted_at else None,
                }
                for item in result.items
            ],
            'total_count': result.total_count,
        })
