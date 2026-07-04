"""
Attendance Service — Domain Service for marking attendance
"""

import logging
from typing import List
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.dispatch import Signal

from src.backend.mentorship.domain.models.attendance import Attendance
from src.backend.mentorship.domain.models.offline_session import OfflineSession
from src.backend.mentorship.domain.models.student_group import StudentMentorGroup

User = get_user_model()
logger = logging.getLogger(__name__)


attendance_marked = Signal()  


class AttendanceService:
    """
    Domain service for attendance management.

    Responsibilities:
    - Mark attendance for students (single or bulk)
    - Validate attendance marking rules
    - Emit AttendanceMarked events
    """

    @staticmethod
    @transaction.atomic
    def mark_attendance(
        session_id: UUID,
        student_id: UUID,
        status: str,
        marked_by_id: UUID,
        notes: str = None,
    ) -> Attendance:
        """
        Mark attendance for a single student.

        Returns Attendance record.
        Emits AttendanceMarked event (→ Progress Domain).
        """

        
        try:
            session = OfflineSession.objects.select_for_update().get(id=session_id)
        except OfflineSession.DoesNotExist:
            raise ValueError(f"Session {session_id} not found")

        
        if not session.can_mark_attendance():
            raise ValueError(
                f"Cannot mark attendance for session {session_id} "
                f"(status: {session.status})"
            )

        
        membership = StudentMentorGroup.objects.filter(
            student_id=student_id,
            group=session.group,
            left_at__isnull=True  
        ).first()

        if not membership:
            raise ValueError(
                f"Student {student_id} is not in group {session.group_id}"
            )

        
        attendance, created = Attendance.objects.update_or_create(
            session=session,
            student_id=student_id,
            defaults={
                'status': status,
                'marked_by_id': marked_by_id,
                'marked_at': timezone.now(),
                'notes': notes,
            }
        )

        logger.info(
            f"Attendance {'created' if created else 'updated'}: "
            f"{attendance.id} for student {student_id} in session {session_id}"
        )

        
        if attendance.counts_as_present and session.lesson_id:
            transaction.on_commit(lambda: attendance_marked.send(
                sender=Attendance,
                attendance_id=attendance.id,
                session_id=session.id,
                student_id=student_id,
                enrollment_id=membership.enrollment_id,
                lesson_id=session.lesson_id,
                status=status,
                marked_by_id=marked_by_id,
            ))

        return attendance

    @staticmethod
    @transaction.atomic
    def bulk_mark_attendance(
        session_id: UUID,
        attendance_records: List[dict],
        marked_by_id: UUID,
    ) -> List[Attendance]:
        """
        Mark attendance for multiple students at once.

        attendance_records format:
        [
            {'student_id': UUID, 'status': 'present', 'notes': '...'},
            {'student_id': UUID, 'status': 'absent', 'notes': '...'},
        ]

        Returns list of Attendance records.
        """

        attendances = []

        for record in attendance_records:
            attendance = AttendanceService.mark_attendance(
                session_id=session_id,
                student_id=record['student_id'],
                status=record['status'],
                marked_by_id=marked_by_id,
                notes=record.get('notes'),
            )
            attendances.append(attendance)

        logger.info(
            f"Bulk attendance marked: {len(attendances)} records "
            f"for session {session_id}"
        )

        return attendances
