"""
Submit Revision API View

POST /api/v1/submissions/{id}/revisions/ - Submit new revision
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.commands import (
    SubmitRevisionCommand,
    SubmitRevisionHandler
)
from src.backend.submissions.application.queries import GetSubmissionDetailQuery
from src.backend.submissions.presentation.rest.submissions.serializers import (
    SubmitRevisionSerializer,
    SubmissionDetailSerializer
)


class SubmitRevisionView(APIView):
    """
    Submit new revision for submission.

    POST /api/v1/submissions/{id}/revisions/

    Permissions: IsAuthenticated (Student, owner only)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, submission_id):
        serializer = SubmitRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            command = SubmitRevisionCommand(
                submission_id=submission_id,
                student_id=request.user.id,
                submission_type=serializer.validated_data['submission_type'],
                payload=serializer.validated_data['payload'],
                notes=serializer.validated_data.get('notes', '')
            )

            revision = SubmitRevisionHandler.handle(command)

            
            detail_dto = GetSubmissionDetailQuery.execute(submission_id)
            response_serializer = SubmissionDetailSerializer(detail_dto)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
