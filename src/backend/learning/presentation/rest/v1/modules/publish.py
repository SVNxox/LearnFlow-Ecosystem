"""
Module Publish/Unpublish API — публикация/снятие с публикации модуля.

Endpoints:
- POST /api/v1/learning/modules/{module_id}/publish/ — публикация модуля
- POST /api/v1/learning/modules/{module_id}/unpublish/ — снятие с публикации

Permissions: Admin, Staff, or Course Author
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import UpdateModuleCommand

logger = logging.getLogger(__name__)


class ModulePublishView(APIView):
    """
    POST /api/v1/learning/modules/{module_id}/publish/ — публикация модуля.

    Path Parameters:
    - module_id: UUID модуля

    Business Rules:
    - Модуль должен иметь минимум 1 опубликованный урок
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, module_id: str) -> Response:
        """Публикует модуль."""

        try:
            
            module = UpdateModuleCommand.publish_module(
                module_id=module_id, actor=request.user
            )

            response_data = {
                "id": str(module.id),
                "title": module.title,
                "is_published": module.is_published,
                "message": "Module published successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error publishing module: {e.code}")
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
                f"Unexpected error publishing module: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while publishing the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ModuleUnpublishView(APIView):
    """
    POST /api/v1/learning/modules/{module_id}/unpublish/ — снятие с публикации.

    Path Parameters:
    - module_id: UUID модуля
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, module_id: str) -> Response:
        """Снимает модуль с публикации."""

        try:
            
            module = UpdateModuleCommand.unpublish_module(
                module_id=module_id, actor=request.user
            )

            response_data = {
                "id": str(module.id),
                "title": module.title,
                "is_published": module.is_published,
                "message": "Module unpublished successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error unpublishing module: {e.code}")
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
                f"Unexpected error unpublishing module: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while unpublishing the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )