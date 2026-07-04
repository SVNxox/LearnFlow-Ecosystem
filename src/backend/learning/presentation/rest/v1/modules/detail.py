"""
Module Detail API — просмотр, обновление и удаление модуля.

Endpoints:
- GET    /api/v1/learning/modules/{module_id}/ — детали модуля (публичный)
- PATCH  /api/v1/learning/modules/{module_id}/ — обновление модуля (админский)
- DELETE /api/v1/learning/modules/{module_id}/ — удаление модуля (админский)
"""

import logging
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import UpdateModuleCommand, UpdateModuleData
from src.backend.learning.domain.models import Module

logger = logging.getLogger(__name__)


class ModuleDetailView(APIView):
    """
    Детали модуля. Поддерживает GET, PATCH, DELETE.

    - GET: публичный доступ с проверкой видимости
    - PATCH/DELETE: только admin/staff/course author
    """

    def get_permissions(self):
        """
        Разные права для разных методов:
        - GET: AllowAny (с проверкой visibility внутри)
        - PATCH/DELETE: IsAuthenticated + IsAdminOrStaff
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrStaff()]

    def get(self, request: Request, module_id: str) -> Response:
        """
        Возвращает детальную информацию о модуле.

        Visibility:
        - Unauthenticated: только published модуль в published курсе
        - Authenticated: published модуль
        - Admin/Staff/Author: все статусы
        """
        try:
            module = (
                Module.objects.select_related("course")
                .prefetch_related("lessons")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            return Response(
                {"detail": "Module not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        user = request.user if request.user.is_authenticated else None
        user_roles = []
        if user and hasattr(user, 'get_roles'):
            try:
                user_roles = user.get_roles()
            except Exception:
                user_roles = []

        is_admin_or_staff = 'admin' in user_roles or 'staff' in user_roles
        is_course_author = module.course.created_by_id == user.id if user else False

        
        if not (is_admin_or_staff or is_course_author):
            if not module.is_published:
                return Response(
                    {"detail": "Module not found or not accessible."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            if module.course.status != "published":
                return Response(
                    {"detail": "Module not found or not accessible."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        
        response_data = {
            "id": str(module.id),
            "title": module.title,
            "description": module.description,
            "order": module.order,
            "estimated_hours": module.estimated_hours,
            "is_published": module.is_published,
            "course_id": str(module.course_id),
            "lesson_count": module.lessons.filter(deleted_at__isnull=True).count(),
            "lessons": [
                {
                    "id": str(lesson.id),
                    "title": lesson.title,
                    "order": lesson.order,
                    "estimated_minutes": lesson.estimated_minutes,
                    "is_published": lesson.is_published,
                    "is_free_preview": lesson.is_free_preview,
                    "has_homework": hasattr(lesson, 'homework') and lesson.homework is not None,
                    "has_quiz": hasattr(lesson, 'quiz') and lesson.quiz is not None,
                    "has_practice": lesson.practice_items.exists() if hasattr(lesson, 'practice_items') else False,
                }
                for lesson in module.lessons.filter(deleted_at__isnull=True).order_by('order')
            ],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request: Request, module_id: str) -> Response:
        """
        Обновляет модуль.

        Permissions: Admin, Staff, or Course Author
        """
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
            logger.error(f"Unexpected error updating module: {type(e).__name__}: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e) or "An unexpected error occurred while updating the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request: Request, module_id: str) -> Response:
        """
        Удаляет модуль (soft delete).

        Permissions: Admin, Staff, or Course Author
        """
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
        except Exception as e:
            logger.error(f"Unexpected error deleting module: {type(e).__name__}: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e) or "An unexpected error occurred while deleting the module."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )