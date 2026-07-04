"""
Mark attendance endpoint — POST /api/v1/mentorship/sessions/{id}/attendance/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.mentorship.application.commands import (
    MarkAttendanceCommand,
    MarkAttendanceHandler,
)
from src.backend.mentorship.presentation.rest.v1.serializers import (
    MarkAttendanceSerializer,
    AttendanceSerializer,
)


class MarkAttendanceView(APIView):
    """Mark attendance for a student."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=MarkAttendanceSerializer,
        responses={201: AttendanceSerializer},
        tags=['Mentorship — Attendance'],
        operation_id='mark_attendance',
        description='Mark attendance for a student in an offline session (mentor only)',
    )
    def post(self, request: Request, session_id: str) -> Response:
        """Mark attendance."""

        serializer = MarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command = MarkAttendanceCommand(
            session_id=UUID(session_id),
            student_id=serializer.validated_data['student_id'],
            status=serializer.validated_data['status'],
            marked_by_id=request.user.id,
            notes=serializer.validated_data.get('notes'),
        )

        handler = MarkAttendanceHandler()

        try:
            attendance = handler.handle(command)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = AttendanceSerializer(attendance)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
