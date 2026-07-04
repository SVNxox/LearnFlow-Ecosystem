"""
Course Categories API — управление категориями курсов.

Endpoints:
- GET    /api/v1/learning/categories/ — список категорий
- POST   /api/v1/learning/categories/ — создать категорию
- GET    /api/v1/learning/categories/{id}/ — детали категории
- PATCH  /api/v1/learning/categories/{id}/ — обновить категорию
- DELETE /api/v1/learning/categories/{id}/ — удалить категорию
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.learning.domain.models import CourseCategory, Course
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


def _serialize_category(category: CourseCategory) -> dict:
    """Сериализует категорию со всеми полями."""
    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
        "description": category.description or "",
        "icon": category.icon or "",
        "order": category.order,
        "is_active": category.is_active,
        "parent_id": str(category.parent_id) if category.parent_id else None,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }


class CategoryListView(APIView):
    """GET + POST для списка категорий."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        """Возвращает список всех категорий."""
        try:
            categories = CourseCategory.objects.all().order_by("order", "name")
            data = [_serialize_category(cat) for cat in categories]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing categories: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request) -> Response:
        """Создаёт новую категорию."""
        data = request.data

        
        if not data.get("name"):
            return Response(
                {"detail": "Category name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = CourseCategory.objects.create(
                name=data["name"],
                slug=data.get("slug", ""),
                description=data.get("description", ""),
                icon=data.get("icon", ""),
                order=data.get("order", 0),
                is_active=data.get("is_active", True),
                parent_id=data.get("parent_id"),
            )
            return Response(_serialize_category(category), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    """GET + PATCH + DELETE для конкретной категории."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, category_id: str) -> Response:
        """Возвращает детали категории."""
        try:
            category = get_object_or_404(CourseCategory, id=category_id)
            return Response(_serialize_category(category), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting category: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request: Request, category_id: str) -> Response:
        """Обновляет категорию (частичное обновление)."""
        try:
            category = get_object_or_404(CourseCategory, id=category_id)
        except Exception:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        update_fields = []

        
        if "name" in data:
            name = data["name"]
            if len(name) > 100:
                return Response(
                    {"detail": "Category name must be at most 100 characters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.name = name
            update_fields.append("name")

        if "slug" in data:
            slug = data["slug"]
            if len(slug) > 100:
                return Response(
                    {"detail": "Category slug must be at most 100 characters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.slug = slug
            update_fields.append("slug")

        if "description" in data:
            description = data["description"]
            if len(description) > 500:
                return Response(
                    {"detail": "Category description must be at most 500 characters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.description = description
            update_fields.append("description")

        if "icon" in data:
            icon = data["icon"]
            if len(icon) > 500:
                return Response(
                    {"detail": "Category icon must be at most 500 characters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.icon = icon
            update_fields.append("icon")

        if "order" in data:
            category.order = data["order"]
            update_fields.append("order")

        if "is_active" in data:
            category.is_active = data["is_active"]
            update_fields.append("is_active")

        if "parent_id" in data:
            category.parent_id = data["parent_id"]
            update_fields.append("parent_id")

        if update_fields:
            try:
                category.save(update_fields=update_fields)
            except Exception as e:
                logger.error(f"Error saving category: {e}", exc_info=True)
                return Response(
                    {"detail": f"Error saving category: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(_serialize_category(category), status=status.HTTP_200_OK)

    def delete(self, request: Request, category_id: str) -> Response:
        """Удаляет категорию."""
        try:
            category = get_object_or_404(CourseCategory, id=category_id)
        except Exception:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        
        courses_count = Course.objects.filter(category_id=category_id).count()

        if courses_count > 0:
            return Response(
                {"detail": f"Cannot delete category: {courses_count} course(s) exist in this category"},
                status=status.HTTP_400_BAD_REQUEST
            )

        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)