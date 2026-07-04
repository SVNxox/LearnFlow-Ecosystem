"""
POST /api/v1/identity/auth/login/
"""
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import login_user
from src.backend.core.exceptions import AuthError
from src.backend.core.i18n import get_language_from_request
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import LoginRequestSerializer, LoginResponseSerializer


@extend_schema(tags=['Identity — Auth'])
class LoginView(APIView):
    """Login endpoint — email + password authentication."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_login',
        summary='Login',
        description=(
            'Authenticate with email + password. Returns a short-lived access token '
            '(15 min, RS256 JWT) and a long-lived refresh token (30 days). '
            'Enforces account lockout after 5 failed attempts.'
        ),
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            401: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'student@example.com',
                    'password': 'SecurePass123!'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Login Success',
                value={
                    'access_token': 'eyJhbGc...',
                    'refresh_token': 'dGhpcyBpcyBh...',
                    'token_type': 'Bearer',
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lang = get_language_from_request(request)

        try:
            result = login_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                request=request,
                lang=lang,
            )
        except AuthError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'token_type': result['token_type'],
            },
            status=status.HTTP_200_OK,
        )