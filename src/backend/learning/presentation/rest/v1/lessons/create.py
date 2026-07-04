"""
Lesson Create API — создание нового урока.

Endpoint: POST /api/learning/{course_id}/modules/{module_id}/lessons/
Permissions: IsStaff or IsAuthor
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError, PermissionDenied

from src.backend.learning.application.commands import CreateLessonCommand, CreateLessonData


class LessonCreateView(APIView):
    """
    POST /api/learning/lessons/create/ — создание урока.

    Permissions: Staff or Course Author

    Request Body:
    {
        "module_id": str (required, UUID),
        "title": str (required),
        "description": str (optional),
        "estimated_minutes": int (optional),
        "is_free_preview": bool (default false)
    }

    Response: Created lesson
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Создаёт новый урок в модуле."""

        
        data = request.data
        module_id = data.get("module_id")

        if not module_id:
            return Response(
                {"detail": "module_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            command_data = CreateLessonData(
                title=data.get("title"),
                description=data.get("description"),
                estimated_minutes=data.get("estimated_minutes"),
                is_free_preview=data.get("is_free_preview", False),
            )

            
            lesson = CreateLessonCommand.execute(
                module_id=module_id, data=command_data, actor=request.user
            )

            
            response_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "description": lesson.description,
                "estimated_minutes": lesson.estimated_minutes,
                "is_free_preview": lesson.is_free_preview,
                "order": lesson.order,
                "is_published": lesson.is_published,
                "module_id": str(lesson.module_id),
                "created_at": lesson.created_at.isoformat(),
                "updated_at": lesson.updated_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"detail": "An error occurred while creating the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
