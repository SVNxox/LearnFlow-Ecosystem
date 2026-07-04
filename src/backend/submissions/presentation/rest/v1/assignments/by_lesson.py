"""
GET /api/v1/submissions/assignments/by-lesson/{lesson_id}/

Get assignment for a specific lesson.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.backend.submissions.domain.models import Assignment


class AssignmentByLessonView(APIView):
    """
    Get assignment for a lesson.

    Returns assignment details if one exists for this lesson.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        """
        GET /api/v1/submissions/assignments/by-lesson/{lesson_id}/

        Returns assignment or 404 if not found.
        """
        
        assignment = Assignment.objects.filter(
            lesson_id=lesson_id
        ).order_by('-created_at').first()

        if not assignment:
            return Response(
                {"detail": "Assignment not found for this lesson"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'id': str(assignment.id),
            'lesson_id': str(assignment.lesson_id) if assignment.lesson_id else None,
            'assessment_item_id': str(assignment.assessment_item_id) if assignment.assessment_item_id else None,
            'type': assignment.type,
            'title': assignment.title,
            'description': assignment.description,
            'max_score': float(assignment.max_score),
            'deadline_offset_days': assignment.deadline_offset_days,
            'submission_types_allowed': assignment.submission_types_allowed,
            'allowed_file_extensions': assignment.allowed_file_extensions,
            'max_file_size_mb': assignment.max_file_size_mb,
            'auto_check_enabled': assignment.auto_check_enabled,
            'created_at': assignment.created_at.isoformat(),
        })