"""
POST /api/v1/assessment/reviews/{response_id}/

Submit mentor review for a response.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from decimal import Decimal

from src.backend.assessment.domain.services import MentorReviewService


class SubmitReviewView(APIView):
    """
    Submit mentor review.

    Mentor grades text_answer/interview/project or overrides auto-grade.
    """
    permission_classes = [IsAuthenticated]
    

    def post(self, request, response_id):
        """
        POST /api/v1/assessment/reviews/{response_id}/

        Body:
        {
            "points": 8.5,
            "comment": "Good answer but missing key points"
        }

        Returns:
        {
            "response_id": "uuid",
            "final_points": 8.5,
            "reviewed_at": "2026-06-09T16:00:00Z"
        }
        """
        points = request.data.get('points')
        comment = request.data.get('comment', '')

        if points is None:
            return Response(
                {'error': 'points required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            points = Decimal(str(points))

            
            MentorReviewService.submit_manual_grade(
                response_id=response_id,
                mentor_id=request.user.id,
                points=points,
                comment=comment
            )

            
            from src.backend.assessment.domain.models import AssessmentResponse
            response = AssessmentResponse.objects.get(id=response_id)

            return Response({
                'response_id': str(response.id),
                'final_points': float(response.final_points),
                'reviewed_at': response.reviewed_at.isoformat() if response.reviewed_at else None,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
