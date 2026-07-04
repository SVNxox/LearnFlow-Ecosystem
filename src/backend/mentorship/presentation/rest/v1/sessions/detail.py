"""
Session detail endpoint — GET /api/v1/mentorship/sessions/{id}/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.mentorship.application.queries import (
    SessionDetailQuery,
    SessionDetailQueryHandler,
)
from src.backend.mentorship.presentation.rest.v1.serializers import SessionDetailSerializer


class SessionDetailView(APIView):
    """Retrieve session details with attendances."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: SessionDetailSerializer},
        tags=['Mentorship — Sessions'],
        operation_id='get_session',
        description='Retrieve session details with attendance records',
    )
    def get(self, request: Request, session_id: str) -> Response:
        """Get session details."""

        query = SessionDetailQuery(session_id=UUID(session_id))

        handler = SessionDetailQueryHandler()

        try:
            session = handler.handle(query)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        
        if not request.user.is_staff:
            if session.group.mentor_id != request.user.id:
                return Response(
                    {'detail': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = SessionDetailSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
