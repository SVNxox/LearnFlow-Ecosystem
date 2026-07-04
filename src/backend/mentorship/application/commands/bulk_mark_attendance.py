"""
Bulk Mark Attendance Command
"""

from dataclasses import dataclass
from typing import List
from uuid import UUID

from src.backend.mentorship.domain.services.attendance_service import AttendanceService
from src.backend.mentorship.domain.models.attendance import Attendance


@dataclass
class BulkMarkAttendanceCommand:
    """Command to mark attendance for multiple students."""

    session_id: UUID
    attendance_records: List[dict]  
    marked_by_id: UUID


class BulkMarkAttendanceHandler:
    """Handler for BulkMarkAttendanceCommand."""

    def handle(self, command: BulkMarkAttendanceCommand) -> List[Attendance]:
        """Mark attendance for multiple students."""

        return AttendanceService.bulk_mark_attendance(
            session_id=command.session_id,
            attendance_records=command.attendance_records,
            marked_by_id=command.marked_by_id,
        )
