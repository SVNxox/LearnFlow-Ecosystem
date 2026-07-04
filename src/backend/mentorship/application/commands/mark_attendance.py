"""
Mark Attendance Command
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.backend.mentorship.domain.services.attendance_service import AttendanceService
from src.backend.mentorship.domain.models.attendance import Attendance


@dataclass
class MarkAttendanceCommand:
    """Command to mark attendance for a student."""

    session_id: UUID
    student_id: UUID
    status: str  
    marked_by_id: UUID
    notes: Optional[str] = None


class MarkAttendanceHandler:
    """Handler for MarkAttendanceCommand."""

    def handle(self, command: MarkAttendanceCommand) -> Attendance:
        """Mark attendance."""

        return AttendanceService.mark_attendance(
            session_id=command.session_id,
            student_id=command.student_id,
            status=command.status,
            marked_by_id=command.marked_by_id,
            notes=command.notes,
        )
