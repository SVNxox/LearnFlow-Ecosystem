"""
My Submissions API View

GET /api/v1/submissions/my/ - Get student's submissions
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.queries import GetMySubmissionsQuery
from src.backend.submissions.presentation.rest.submissions.serializers import (
    MySubmissionSerializer
)


class MySubmissionsView(APIView):
    """
    Get student's submissions.

    GET /api/v1/submissions/my/
    Query params:
    - enrollment_id (optional): filter by course enrollment

    Permissions: IsAuthenticated (Student)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollment_id = request.query_params.get('enrollment_id')

        submissions = GetMySubmissionsQuery.execute(
            student_id=request.user.id,
            enrollment_id=enrollment_id
        )

        serializer = MySubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
