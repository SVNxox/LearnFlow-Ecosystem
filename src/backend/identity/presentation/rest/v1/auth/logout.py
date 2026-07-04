"""
identity/presentation/rest/v1/auth/logout.py

POST /api/v1/identity/auth/logout/
POST /api/v1/identity/auth/logout/all/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import logout_user, logout_all_sessions
from .serializers import LogoutRequestSerializer


@extend_schema(tags=['Identity — Auth'])
class LogoutView(APIView):
    """Logout — revoke a single refresh token."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_auth_logout',
        summary='Logout (revoke refresh token)',
        description='Revokes the provided refresh token. Access token expires naturally.',
        request=LogoutRequestSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LogoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logout_user(serializer.validated_data['refresh_token'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Identity — Auth'])
class LogoutAllView(APIView):
    """Logout from all devices — revoke all refresh tokens."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_auth_logout_all',
        summary='Logout from all devices',
        description='Revokes all active refresh tokens for the authenticated user.',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'revoked': {'type': 'integer'}
                }
            }
        },
    )
    def post(self, request):
        count = logout_all_sessions(request.user)
        return Response({'revoked': count}, status=status.HTTP_200_OK)
