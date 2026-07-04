"""
Module Reorder API — переупорядочивание модулей.

Endpoint: POST /api/learning/{course_id}/modules/reorder/
Permissions: IsStaff or IsAuthor
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError, PermissionDenied

from src.backend.learning.application.commands import UpdateModuleCommand


class ModuleReorderView(APIView):
    """
    POST /api/learning/{course_id}/modules/reorder/ — переупорядочивание модулей.

    Permissions: Staff or Course Author

    Path Parameters:
    - course_id: UUID курса

    Request Body:
    {
        "ordered_ids": ["module_id_1", "module_id_2", ...]
    }

    Business Rules:
    - ordered_ids должен содержать ВСЕ non-deleted module IDs курса

    Response: List[Module] в новом порядке
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, course_id: str) -> Response:
        """Переупорядочивает модули."""

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
            
            modules = UpdateModuleCommand.reorder_modules(
                course_id=course_id, ordered_ids=ordered_ids, actor=request.user
            )

            
            response_data = [
                {
                    "id": str(m.id),
                    "title": m.title,
                    "order": m.order,
                }
                for m in modules
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"detail": "An error occurred while reordering modules."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
