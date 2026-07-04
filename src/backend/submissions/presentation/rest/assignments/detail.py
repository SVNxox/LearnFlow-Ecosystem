"""
Assignment Detail API — получение, обновление и удаление задания.

Endpoints:
- GET    /api/v1/submissions/assignments/{assignment_id}/ — получить
- PATCH  /api/v1/submissions/assignments/{assignment_id}/ — обновить
- DELETE /api/v1/submissions/assignments/{assignment_id}/ — удалить
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.submissions.domain.models.assignment import Assignment
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


def _serialize_assignment(assignment: Assignment) -> dict:
    """Сериализует assignment."""
    return {
        "id": str(assignment.id),
        "lesson_id": str(assignment.lesson_id) if assignment.lesson_id else None,
        "assessment_item_id": str(assignment.assessment_item_id) if assignment.assessment_item_id else None,
        "type": assignment.type,
        "title": assignment.title,
        "description": assignment.description,
        "max_score": float(assignment.max_score),
        "deadline_offset_days": assignment.deadline_offset_days,
        "submission_types_allowed": assignment.submission_types_allowed,
        "allowed_file_extensions": assignment.allowed_file_extensions,
        "max_file_size_mb": assignment.max_file_size_mb,
        "auto_check_enabled": assignment.auto_check_enabled,
        "created_at": assignment.created_at.isoformat(),
    }


class AssignmentDetailView(APIView):
    """
    GET, PATCH, DELETE для assignment по ID.

    ✅ Теперь поддерживает все три метода!
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, assignment_id: str) -> Response:
        """Получить assignment по ID."""
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(_serialize_assignment(assignment), status=status.HTTP_200_OK)

    def patch(self, request: Request, assignment_id: str) -> Response:
        """Обновить assignment (частичное обновление)."""
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        update_fields = []

        
        if "title" in data:
            assignment.title = data["title"]
            update_fields.append("title")

        if "description" in data:
            assignment.description = data["description"]
            update_fields.append("description")

        if "type" in data:
            assignment.type = data["type"]
            update_fields.append("type")

        if "max_score" in data:
            assignment.max_score = data["max_score"]
            update_fields.append("max_score")

        if "deadline_offset_days" in data:
            assignment.deadline_offset_days = data["deadline_offset_days"]
            update_fields.append("deadline_offset_days")

        if "submission_types_allowed" in data:
            assignment.submission_types_allowed = data["submission_types_allowed"]
            update_fields.append("submission_types_allowed")

        if "allowed_file_extensions" in data:
            assignment.allowed_file_extensions = data["allowed_file_extensions"]
            update_fields.append("allowed_file_extensions")

        if "max_file_size_mb" in data:
            assignment.max_file_size_mb = data["max_file_size_mb"]
            update_fields.append("max_file_size_mb")

        if "auto_check_enabled" in data:
            assignment.auto_check_enabled = data["auto_check_enabled"]
            update_fields.append("auto_check_enabled")

        if update_fields:
            assignment.save(update_fields=update_fields)

        return Response(_serialize_assignment(assignment), status=status.HTTP_200_OK)

    def delete(self, request: Request, assignment_id: str) -> Response:
        """Удалить assignment."""
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        
        from src.backend.submissions.domain.models import Submission
        submissions_count = Submission.objects.filter(assignment=assignment).count()

        if submissions_count > 0:
            return Response(
                {
                    "detail": f"Cannot delete assignment: {submissions_count} submission(s) exist. "
                              "Delete or reassign submissions first."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            assignment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting assignment: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )