"""
Module Update/Delete API — обновление и удаление модуля (админка).

Endpoints:
- PATCH /api/v1/learning/admin/modules/{module_id}/ — обновление
- DELETE /api/v1/learning/admin/modules/{module_id}/ — удаление

Permissions: Admin, Staff, or Course Author
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import UpdateModuleCommand, UpdateModuleData

logger = logging.getLogger(__name__)


class ModuleUpdateView(APIView):
    """
    PATCH /api/v1/learning/admin/modules/{module_id}/ — обновление модуля.
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def patch(self, request: Request, module_id: str) -> Response:
        """Обновляет модуль."""

        data = request.data

        try:
            command_data = UpdateModuleData(
                title=data.get("title"),
                description=data.get("description"),
                estimated_hours=data.get("estimated_hours"),
            )

            module = UpdateModuleCommand.execute(
                module_id=module_id, data=command_data, actor=request.user
            )

            response_data = {
                "id": str(module.id),
                "title": module.title,
                "description": module.description,
                "estimated_hours": module.estimated_hours,
                "order": module.order,
                "is_published": module.is_published,
                "course_id": str(module.course_id),
                "created_at": module.created_at.isoformat(),
                "updated_at": module.updated_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error: {e.code}")
            return Response(
                {"detail": str(e.message) if hasattr(e, 'message') else str(e), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )

        except NotFoundError as e:
            logger.warning(f"Not found error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except AccessDeniedError as e:
            logger.warning(f"Access denied error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(
                f"Unexpected error updating module: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": str(e) or "An unexpected error occurred while updating the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ModuleDeleteView(APIView):
    """
    DELETE /api/v1/learning/admin/modules/{module_id}/ — удаление модуля (soft delete).

    Permissions: Admin, Staff, or Course Author
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def delete(self, request: Request, module_id: str) -> Response:
        """Удаляет модуль (soft delete)."""

        try:
            module = UpdateModuleCommand.delete_module(
                module_id=module_id, actor=request.user
            )

            response_data = {
                "id": str(module.id),
                "title": module.title,
                "deleted_at": module.deleted_at.isoformat() if module.deleted_at else None,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except NotFoundError as e:
            logger.warning(f"Not found error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except AccessDeniedError as e:
            logger.warning(f"Access denied error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except DjangoValidationError as e:
            logger.warning(f"Django validation error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                f"Unexpected error deleting module: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": str(e) or "An unexpected error occurred while deleting the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )