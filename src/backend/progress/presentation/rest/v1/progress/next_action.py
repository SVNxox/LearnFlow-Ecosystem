"""
GET /api/v1/progress/courses/{enrollment_id}/next/

Returns what student should do next in their learning journey.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.progress.domain.models import CourseProgress
from src.backend.progress.application.queries import GetNextActionQuery


class NextActionView(APIView):
    """
    Get next action for student.

    Returns the next lesson to study or assessment to take.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id):
        """
        GET /api/v1/progress/courses/{enrollment_id}/next/

        Returns:
        {
            "action_type": "study_lesson|take_assessment|course_completed|blocked",
            "lesson_id": "uuid",  // if action_type = study_lesson
            "module_id": "uuid",
            "assessment_id": "uuid",  // if action_type = take_assessment
            "message": "Continue studying Module 2, Lesson 3"
        }
        """
        
        progress = get_object_or_404(
            CourseProgress,
            enrollment_id=enrollment_id,
            user_id=request.user.id
        )

        query = GetNextActionQuery(enrollment_id=enrollment_id)
        result = query.execute()

        response_data = {
            'action_type': result.action_type,
            'message': result.message,
        }

        if result.lesson_id:
            response_data['lesson_id'] = str(result.lesson_id)
        if result.module_id:
            response_data['module_id'] = str(result.module_id)
        if result.assessment_id:
            response_data['assessment_id'] = str(result.assessment_id)

        return Response(response_data)
