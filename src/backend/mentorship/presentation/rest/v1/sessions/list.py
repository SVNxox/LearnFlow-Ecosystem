"""
Group sessions list endpoint — GET /api/v1/mentorship/groups/{group_id}/sessions/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.mentorship.application.queries import (
    MyGroupSessionsQuery,
    MyGroupSessionsQueryHandler,
)
from src.backend.mentorship.presentation.rest.v1.serializers import SessionListSerializer


class MyGroupSessionsListView(APIView):
    """List sessions for mentor's group."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: SessionListSerializer(many=True)},
        tags=['Mentorship — Sessions'],
        operation_id='list_group_sessions',
        description='List all sessions for a mentor group',
    )
    def get(self, request: Request, group_id: str) -> Response:
        """List group sessions."""

        query = MyGroupSessionsQuery(
            mentor_id=request.user.id,
            group_id=UUID(group_id),
        )

        handler = MyGroupSessionsQueryHandler()
        sessions = handler.handle(query)

        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
