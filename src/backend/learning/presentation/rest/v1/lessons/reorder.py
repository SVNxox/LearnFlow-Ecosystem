"""
Lesson Reorder API — переупорядочивание уроков.

Endpoint: POST /api/learning/{course_id}/modules/{module_id}/lessons/reorder/
Permissions: IsStaff or IsAuthor
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError, PermissionDenied

from src.backend.learning.application.commands import UpdateLessonCommand


class LessonReorderView(APIView):
    """
    POST /api/learning/{course_id}/modules/{module_id}/lessons/reorder/
    — переупорядочивание уроков.

    Permissions: Staff or Course Author

    Path Parameters:
    - course_id: UUID курса
    - module_id: UUID модуля

    Request Body:
    {
        "ordered_ids": ["lesson_id_1", "lesson_id_2", ...]
    }

    Business Rules:
    - ordered_ids должен содержать ВСЕ non-deleted lesson IDs модуля

    Response: List[Lesson] в новом порядке
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, course_id: str, module_id: str) -> Response:
        """Переупорядочивает уроки."""

        ordered_ids = request.data.get("ordered_ids")

        if not ordered_ids:
            return Response(
                {"detail": "ordered_ids is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(ordered_ids, list):
            return Response(
                {"detail": "ordered_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(ordered_ids) == 0:
            return Response(
                {"detail": "ordered_ids cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            
            lessons = UpdateLessonCommand.reorder_lessons(
                module_id=module_id, ordered_ids=ordered_ids, actor=request.user
            )

            
            response_data = [
                {
                    "id": str(l.id),
                    "title": l.title,
                    "order": l.order,
                }
                for l in lessons
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"detail": "An error occurred while reordering lessons."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
