"""
Lesson Practice API — управление практическими заданиями.
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import ManagePracticeCommand, AddPracticeData, UpdatePracticeData
from src.backend.learning.domain.models import LessonPractice

logger = logging.getLogger(__name__)


def _serialize_practice(item: LessonPractice) -> dict:
    return {
        "id": str(item.id),
        "title": item.title,
        "description": item.description or "",
        "instructions": item.instructions or "",
        "type": item.type,
        "starter_code": item.starter_code or "",
        "solution_code": item.solution_code or "",
        "language": item.language or "",
        "hints": item.hints or [],
        "max_score": item.max_score,
        "time_limit_minutes": item.time_limit_minutes,
        "order": item.order,
        "lesson_id": str(item.lesson_id),
    }


class LessonPracticeListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, lesson_id: str) -> Response:
        try:
            
            items = LessonPractice.objects.filter(lesson_id=lesson_id).order_by("order")
            data = [_serialize_practice(item) for item in items]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing practice: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request, lesson_id: str) -> Response:
        data = request.data
        try:
            practice_data = AddPracticeData(
                title=data.get("title", ""),
                description=data.get("description"),
                instructions=data.get("instructions"),
                type=data.get("type", "coding"),
                starter_code=data.get("starter_code"),
                solution_code=data.get("solution_code"),
                language=data.get("language"),
                hints=data.get("hints"),
                max_score=data.get("max_score", 10),
                time_limit_minutes=data.get("time_limit_minutes"),
            )
            practice = ManagePracticeCommand.add_practice(
                lesson_id=lesson_id, data=practice_data, actor=request.user
            )
            return Response(_serialize_practice(practice), status=status.HTTP_201_CREATED)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding practice: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonPracticeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def patch(self, request: Request, lesson_id: str, practice_id: str) -> Response:
        data = request.data
        try:
            practice_data = UpdatePracticeData(
                title=data.get("title"),
                description=data.get("description"),
                instructions=data.get("instructions"),
                type=data.get("type"),
                starter_code=data.get("starter_code"),
                solution_code=data.get("solution_code"),
                language=data.get("language"),
                hints=data.get("hints"),
                max_score=data.get("max_score"),
                time_limit_minutes=data.get("time_limit_minutes"),
            )
            practice = ManagePracticeCommand.update_practice(
                practice_id=practice_id, data=practice_data, actor=request.user
            )
            return Response(_serialize_practice(practice), status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating practice: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, lesson_id: str, practice_id: str) -> Response:
        try:
            ManagePracticeCommand.delete_practice(practice_id=practice_id, actor=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting practice: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonPracticeReorderView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        practice_ids = request.data.get("practice_ids", [])
        try:
            items = ManagePracticeCommand.reorder_practice(
                lesson_id=lesson_id, ordered_ids=practice_ids, actor=request.user
            )
            return Response([
                {"id": str(item.id), "order": item.order} for item in items
            ], status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error reordering practice: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)