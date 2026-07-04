"""
Submission Detail API View

GET /api/v1/submissions/{id}/ - Get submission details
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.queries import GetSubmissionDetailQuery
from src.backend.submissions.presentation.rest.submissions.serializers import (
    SubmissionDetailSerializer
)


class SubmissionDetailView(APIView):
    """
    Get submission details with all revisions and reviews.

    GET /api/v1/submissions/{id}/

    Permissions: IsAuthenticated (student can view own, mentor/staff can view all)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, submission_id):
        try:
            detail_dto = GetSubmissionDetailQuery.execute(submission_id)

            
            
            if not request.user.is_staff:
                if detail_dto.student_id != request.user.id:
                    return Response(
                        {"error": "You don't have permission to view this submission"},
                        status=status.HTTP_403_FORBIDDEN
                    )

            serializer = SubmissionDetailSerializer(detail_dto)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
