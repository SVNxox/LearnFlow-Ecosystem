"""
identity/presentation/rest/v1/profile/sessions.py

GET /api/v1/identity/profile/me/sessions/
DELETE /api/v1/identity/profile/me/sessions/{session_id}/
"""
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.models import RefreshToken
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import ActiveSessionSerializer


@extend_schema(tags=['Identity — Sessions'])
class ActiveSessionsView(APIView):
    """List all active sessions for the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_sessions_list',
        summary='List active sessions',
        description='Returns all non-revoked, non-expired refresh tokens for the user.',
        responses={200: ActiveSessionSerializer(many=True)},
    )
    def get(self, request):
        sessions = (
            RefreshToken.objects
            .filter(user=request.user, revoked_at__isnull=True, expires_at__gt=timezone.now())
            .order_by('-created_at')
        )
        serializer = ActiveSessionSerializer(sessions, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Identity — Sessions'])
class RevokeSessionView(APIView):
    """Revoke a specific session by its UUID."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_sessions_revoke',
        summary='Revoke a specific session',
        description='Revoke a refresh token by its UUID. Must belong to the authenticated user.',
        responses={
            204: None,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, session_id):
        try:
            token = RefreshToken.objects.get(
                id=session_id,
                user=request.user,
                revoked_at__isnull=True,
            )
        except RefreshToken.DoesNotExist:
            return Response(
                {'error': 'Session not found.', 'code': 'SESSION_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )

        token.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)
