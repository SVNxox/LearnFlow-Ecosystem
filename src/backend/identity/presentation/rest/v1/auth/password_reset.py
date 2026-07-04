"""
identity/presentation/rest/v1/auth/password_reset.py

POST /api/v1/identity/auth/password-reset/
POST /api/v1/identity/auth/password-reset/confirm/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import request_password_reset, reset_password, AuthError
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer


@extend_schema(tags=['Identity — Password Reset'])
class PasswordResetRequestView(APIView):
    """Request password reset email."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_password_reset',
        summary='Request password reset email',
        description='Sends a reset link to the email. Always returns 200 to prevent email enumeration.',
        request=PasswordResetRequestSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(serializer.validated_data['email'])
        return Response({'detail': 'If that email is registered, a reset link has been sent.'})


@extend_schema(tags=['Identity — Password Reset'])
class PasswordResetConfirmView(APIView):
    """Confirm password reset using token from email."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_password_reset_confirm',
        summary='Confirm password reset',
        description=(
            'Reset password using the token from the email link. '
            'Revokes ALL active sessions after a successful reset.'
        ),
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reset_password(
                raw_token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password'],
            )
        except AuthError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'detail': 'Password updated. Please log in again.'})
