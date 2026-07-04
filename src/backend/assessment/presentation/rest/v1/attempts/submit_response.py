"""
POST /api/v1/assessment/attempts/{attempt_id}/responses/

Submit response to an assessment item.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.assessment.domain.models import AssessmentAttempt
from src.backend.assessment.application.commands import SubmitResponseCommand


class SubmitResponseView(APIView):
    """
    Submit response to assessment item.

    Student answers a question.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        """
        POST /api/v1/assessment/attempts/{attempt_id}/responses/

        Body:
        {
            "item_id": "uuid",
            "selected_option_ids": ["uuid1", "uuid2"],  // for choice items
            "text_response": "text",                     // for text_answer/interview
            "submitted_code": "code",                    // for coding
            "coding_language": "python"                  // for coding
        }

        Returns:
        {
            "response_id": "uuid",
            "is_graded": true,
            "auto_points": 10.00,
            "final_points": 10.00
        }
        """
        
        attempt = get_object_or_404(
            AssessmentAttempt,
            id=attempt_id,
            user_id=request.user.id
        )

        item_id = request.data.get('item_id')
        if not item_id:
            return Response(
                {'error': 'item_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            selected_option_ids = request.data.get('selected_option_ids')
            if selected_option_ids:
                from uuid import UUID
                selected_option_ids = [UUID(opt_id) for opt_id in selected_option_ids]

            command = SubmitResponseCommand(
                attempt_id=attempt_id,
                item_id=item_id,
                selected_option_ids=selected_option_ids,
                text_response=request.data.get('text_response'),
                submitted_code=request.data.get('submitted_code'),
                coding_language=request.data.get('coding_language'),
            )
            response = command.execute()

            return Response({
                'response_id': str(response.id),
                'is_graded': response.is_graded,
                'auto_points': float(response.auto_points) if response.auto_points else None,
                'final_points': float(response.final_points) if response.final_points else None,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
