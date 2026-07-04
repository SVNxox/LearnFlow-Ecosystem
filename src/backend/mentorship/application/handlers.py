"""
Event handler for AttendanceMarked event
"""

import logging
from django.dispatch import receiver

from src.backend.mentorship.domain.services.attendance_service import attendance_marked

logger = logging.getLogger(__name__)


@receiver(attendance_marked)
def handle_attendance_marked(sender, **kwargs):
    """
    Handle AttendanceMarked event.

    Triggers LessonCompleted in Progress Domain (for offline students).

    Event payload:
    - attendance_id: UUID
    - session_id: UUID
    - student_id: UUID
    - enrollment_id: UUID
    - lesson_id: UUID
    - status: str
    - marked_by_id: UUID
    """

    enrollment_id = kwargs.get('enrollment_id')
    lesson_id = kwargs.get('lesson_id')
    student_id = kwargs.get('student_id')
    status = kwargs.get('status')

    logger.info(
        f"AttendanceMarked: student={student_id}, lesson={lesson_id}, status={status}"
    )

    
    
    
    
    
    

    logger.warning(
        f"AttendanceMarked → LessonCompleted integration not implemented yet. "
        f"Enrollment: {enrollment_id}, Lesson: {lesson_id}"
    )
