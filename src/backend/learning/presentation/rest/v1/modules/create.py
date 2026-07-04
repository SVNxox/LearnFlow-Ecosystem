"""
Module Create API — создание нового модуля.

Endpoint: POST /api/learning/{course_id}/modules/
Permissions: IsStaff or IsAuthor
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError, PermissionDenied

from src.backend.learning.application.commands import CreateModuleCommand, CreateModuleData
from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError

logger = logging.getLogger(__name__)


class ModuleCreateView(APIView):
    """
    POST /api/learning/modules/create/ — создание модуля.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Создаёт новый модуль в курсе."""

        data = request.data
        course_id = data.get("course_id")

        if not course_id:
            return Response(
                {"detail": "course_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        title = data.get("title")
        if not title or not title.strip():
            return Response(
                {"detail": "title is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            command_data = CreateModuleData(
                title=title.strip(),
                description=data.get("description", ""),
                estimated_hours=data.get("estimated_hours"),
            )

            module = CreateModuleCommand.execute(
                course_id=course_id, data=command_data, actor=request.user
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

            return Response(response_data, status=status.HTTP_201_CREATED)

        
        except BusinessValidationError as e:
            logger.warning(f"Business validation error: {e.code}")

            
            if e.code == "validation_error":
                
                title = data.get("title", "").strip()
                if len(title) < 3:
                    return Response(
                        {"detail": "Title must be at least 3 characters long"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                estimated_hours = data.get("estimated_hours")
                if estimated_hours is not None and estimated_hours <= 0:
                    return Response(
                        {"detail": "Estimated hours must be greater than 0"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                
                return Response(
                    {"detail": "Invalid data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            return Response(
                {"detail": str(e), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        except NotFoundError as e:
            logger.warning(f"Not found error: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        
        except AccessDeniedError as e:
            logger.warning(f"Access denied error: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except PermissionError as e:
            logger.warning(f"Permission error: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        except Exception as e:
            logger.error(
                f"Unexpected error creating module: {type(e).__name__}: {str(e)}",
                exc_info=True
            )

            error_message = str(e) if str(e) else "An unexpected error occurred while creating the module."

            return Response(
                {"detail": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )