"""
identity/presentation/rest/v1/auth/verify_email.py

GET /api/v1/identity/auth/verify-email/
POST /api/v1/identity/auth/verify-email/resend/
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import verify_email, resend_verification_email, AuthError
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import EmailResendRequestSerializer


@extend_schema(tags=['Identity — Email Verification'])
class EmailVerifyView(APIView):
    """Verify email address using token from verification link."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_verify_email',
        summary='Verify email address',
        description='Activates the account using the token from the verification email link.',
        parameters=[
            OpenApiParameter(
                'token',
                str,
                OpenApiParameter.QUERY,
                required=True,
                description='Raw verification token from email link'
            ),
        ],
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
    def get(self, request):
        raw_token = request.query_params.get('token', '')
        try:
            verify_email(raw_token)
        except AuthError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Email verified. You can now log in.'})


@extend_schema(tags=['Identity — Email Verification'])
class EmailResendView(APIView):
    """Resend verification email (rate-limited)."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_verify_email_resend',
        summary='Resend verification email',
        description='Rate-limited (once per 2 minutes). Always returns 200 to avoid email enumeration.',
        request=EmailResendRequestSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
        },
    )
    def post(self, request):
        serializer = EmailResendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resend_verification_email(serializer.validated_data['email'])
        except AuthError as exc:
            
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response({'detail': 'If that email exists and is unverified, a new link has been sent.'})
