"""
Bulk mark attendance endpoint — POST /api/v1/mentorship/sessions/{id}/attendance/bulk/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.mentorship.application.commands import (
    BulkMarkAttendanceCommand,
    BulkMarkAttendanceHandler,
)
from src.backend.mentorship.presentation.rest.v1.serializers import (
    BulkMarkAttendanceSerializer,
    AttendanceSerializer,
)


class BulkMarkAttendanceView(APIView):
    """Mark attendance for multiple students at once."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BulkMarkAttendanceSerializer,
        responses={201: AttendanceSerializer(many=True)},
        tags=['Mentorship — Attendance'],
        operation_id='bulk_mark_attendance',
        description='Mark attendance for multiple students in one request (mentor only)',
    )
    def post(self, request: Request, session_id: str) -> Response:
        """Bulk mark attendance."""

        serializer = BulkMarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        attendance_records = [
            {
                'student_id': record['student_id'],
                'status': record['status'],
                'notes': record.get('notes'),
            }
            for record in serializer.validated_data['attendances']
        ]

        command = BulkMarkAttendanceCommand(
            session_id=UUID(session_id),
            attendance_records=attendance_records,
            marked_by_id=request.user.id,
        )

        handler = BulkMarkAttendanceHandler()

        try:
            attendances = handler.handle(command)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = AttendanceSerializer(attendances, many=True)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
