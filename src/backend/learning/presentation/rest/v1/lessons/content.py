"""
Lesson Content API — управление контентом урока.

Endpoints:
- GET    /api/v1/learning/lessons/{lesson_id}/content/ — список
- POST   /api/v1/learning/lessons/{lesson_id}/content/ — добавить
- PATCH  /api/v1/learning/lessons/{lesson_id}/content/{content_id}/ — обновить
- DELETE /api/v1/learning/lessons/{lesson_id}/content/{content_id}/ — удалить
- POST   /api/v1/learning/lessons/{lesson_id}/content/reorder/ — переупорядочить
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import ManageContentCommand, AddContentData, UpdateContentData
from src.backend.learning.domain.models import LessonContent

logger = logging.getLogger(__name__)


class LessonContentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, lesson_id: str) -> Response:
        try:
            items = (
                LessonContent.objects.filter(lesson_id=lesson_id)
                .order_by("order")
            )
            data = [
                {
                    "id": str(item.id),
                    "type": item.type,
                    "title": item.title,
                    "description": item.description or '',
                    "url": item.url or '',
                    "body": item.body or '',
                    "duration_seconds": item.duration_seconds,
                    "file_size_bytes": item.file_size_bytes,
                    "metadata": item.metadata or {},
                    "is_required": item.is_required,
                    "is_downloadable": item.is_downloadable,
                    "order": item.order,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
                for item in items
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing content: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request, lesson_id: str) -> Response:
        data = request.data
        try:
            content_data = AddContentData(
                content_type=data.get("type", "text"),
                title=data.get("title"),
                description=data.get("description"),  
                url=data.get("url"),
                body=data.get("body"),
                duration_seconds=data.get("duration_seconds"),
                is_required=data.get("is_required", True),  
                is_downloadable=data.get("is_downloadable", False),
            )
            content = ManageContentCommand.add_content(
                lesson_id=lesson_id, data=content_data, actor=request.user
            )
            return Response({
                "id": str(content.id),
                "type": content.type,
                "title": content.title,
                "description": content.description or '',
                "url": content.url or '',
                "body": content.body or '',
                "duration_seconds": content.duration_seconds,
                "file_size_bytes": content.file_size_bytes,
                "metadata": content.metadata or {},
                "is_required": content.is_required,
                "is_downloadable": content.is_downloadable,
                "order": content.order,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "updated_at": content.updated_at.isoformat() if content.updated_at else None,
            }, status=status.HTTP_201_CREATED)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding content: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonContentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def patch(self, request: Request, lesson_id: str, content_id: str) -> Response:
        data = request.data
        try:
            content_data = UpdateContentData(
                title=data.get("title"),
                description=data.get("description"),  
                url=data.get("url"),
                body=data.get("body"),
                duration_seconds=data.get("duration_seconds"),
                is_required=data.get("is_required"),  
                is_downloadable=data.get("is_downloadable"),  
            )
            content = ManageContentCommand.update_content(
                content_id=content_id, data=content_data, actor=request.user
            )
            return Response({
                "id": str(content.id),
                "type": content.type,  
                "title": content.title,
                "description": content.description,
                "url": content.url,
                "body": content.body,
                "duration_seconds": content.duration_seconds,  
                "order": content.order,
                "is_required": content.is_required,
                "is_downloadable": content.is_downloadable,
            }, status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating content: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, lesson_id: str, content_id: str) -> Response:
        try:
            ManageContentCommand.delete_content(content_id=content_id, actor=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting content: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonContentReorderView(APIView):
    """POST для переупорядочивания контента."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        """Переупорядочивает контент."""
        content_ids = request.data.get("content_ids", [])
        try:
            items = ManageContentCommand.reorder_content(
                lesson_id=lesson_id, ordered_ids=content_ids, actor=request.user
            )
            return Response([
                {"id": str(item.id), "order": item.order} for item in items
            ], status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error reordering content: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)