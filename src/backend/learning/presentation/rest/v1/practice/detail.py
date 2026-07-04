"""
Practice Detail API — просмотр практики и отправка решений.

Endpoints:
- GET    /api/v1/learning/practice/{practice_id}/ — детали практики
- POST   /api/v1/learning/practice/{practice_id}/submit/ — отправка решения
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.learning.domain.models import LessonPractice
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class PracticeDetailView(APIView):
    """Детали практики."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, practice_id: str) -> Response:
        practice = get_object_or_404(LessonPractice, id=practice_id)

        
        if not practice.lesson.is_published:
            user_roles = request.user.get_roles() if hasattr(request.user, 'get_roles') else []
            if not ('admin' in user_roles or 'staff' in user_roles):
                return Response(
                    {"detail": "Practice not accessible."},
                    status=status.HTTP_403_FORBIDDEN
                )

        return Response({
            "id": str(practice.id),
            "title": practice.title,
            "description": practice.description or '',
            "instructions": practice.instructions or '',
            "practice_type": getattr(practice, 'practice_type', 'coding'),
            "starter_code": practice.starter_code or '',
            "solution_code": practice.solution_code or '',
            "language": practice.language or 'python',
            "hints": practice.hints or [],
            "max_score": practice.max_score,
            "time_limit_minutes": practice.time_limit_minutes,
            "lesson_id": str(practice.lesson_id),
            "lesson_title": practice.lesson.title,
            "module_title": practice.lesson.module.title,
            "course_title": practice.lesson.module.course.title,
        }, status=status.HTTP_200_OK)


class PracticeSubmitView(APIView):
    """Отправка решения практики."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, practice_id: str) -> Response:
        practice = get_object_or_404(LessonPractice, id=practice_id)

        code = request.data.get('code', '')
        if not code:
            return Response(
                {"detail": "Code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        

        
        
        
        
        

        return Response({
            "success": True,
            "message": "Решение отправлено на проверку",
            "score": None,  
            "feedback": "Ваше решение получено. Результат будет доступен после проверки ментором.",
        }, status=status.HTTP_200_OK)