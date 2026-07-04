"""
POST /api/v1/progress/lessons/{lesson_id}/content/{content_id}/view/

Records that student has viewed a lesson content item.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.learning.domain.models import Lesson
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.progress.domain.models import LessonProgress
from src.backend.progress.application.commands import RecordContentViewCommand


class RecordContentViewView(APIView):
    """
    Record content view.

    Updates viewed_required_count and checks lesson completion.
    Supports video position tracking.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id, content_id):
        """
        POST /api/v1/progress/lessons/{lesson_id}/content/{content_id}/view/

        Body (optional for video tracking):
        {
            "position_seconds": 120,
            "duration_seconds": 180
        }
        """
        
        lesson = get_object_or_404(
            Lesson.objects.select_related('module'),
            id=lesson_id,
            deleted_at__isnull=True
        )

        
        enrollment = get_object_or_404(
            CourseEnrollment,
            user=request.user,
            course_id=lesson.module.course_id,
            status='active',
            deleted_at__isnull=True
        )

        
        lesson_progress = get_object_or_404(
            LessonProgress,
            enrollment_id=enrollment.id,
            lesson_id=lesson_id
        )

        
        position_seconds = request.data.get('position_seconds')
        duration_seconds = request.data.get('duration_seconds')

        
        command = RecordContentViewCommand(
            enrollment_id=enrollment.id,
            lesson_id=lesson_id,
            content_id=content_id,
            position_seconds=position_seconds,
            duration_seconds=duration_seconds,
        )
        result = command.execute()

        
        lesson_progress.refresh_from_db()

        return Response({
            'status': 'recorded',
            'lesson_completed': result.lesson_completed,
            'viewed_required_count': lesson_progress.viewed_required_count,
            'required_content_count': lesson_progress.required_content_count,
        }, status=status.HTTP_200_OK)