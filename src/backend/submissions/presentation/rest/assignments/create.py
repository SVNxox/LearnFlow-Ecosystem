"""
Assignment API Views

POST /api/v1/assignments/ - Create assignment (staff)
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.application.commands import (
    CreateAssignmentCommand,
    CreateAssignmentHandler
)
from src.backend.submissions.presentation.rest.assignments.serializers import (
    CreateAssignmentSerializer,
    AssignmentDetailSerializer
)


class CreateAssignmentView(APIView):
    """
    Create new assignment.

    POST /api/v1/assignments/

    Permissions: IsStaff
    """
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        serializer = CreateAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command = CreateAssignmentCommand(
            lesson_id=serializer.validated_data.get('lesson_id'),
            assessment_item_id=serializer.validated_data.get('assessment_item_id'),
            type=serializer.validated_data['type'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            max_score=serializer.validated_data['max_score'],
            deadline_offset_days=serializer.validated_data.get('deadline_offset_days'),
            submission_types_allowed=serializer.validated_data['submission_types_allowed'],
            allowed_file_extensions=serializer.validated_data.get('allowed_file_extensions'),
            max_file_size_mb=serializer.validated_data.get('max_file_size_mb', 50),
            auto_check_enabled=serializer.validated_data.get('auto_check_enabled', False),
            auto_check_config=serializer.validated_data.get('auto_check_config'),
            created_by_id=request.user.id
        )

        assignment = CreateAssignmentHandler.handle(command)

        
        from src.backend.submissions.application.queries import (
            GetAssignmentDetailQuery
        )
        detail_dto = GetAssignmentDetailQuery.execute(assignment.id)
        response_serializer = AssignmentDetailSerializer(detail_dto)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
