"""
identity/presentation/rest/v1/auth/register.py

POST /api/v1/identity/auth/register/
"""
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import register_user, AuthError
from src.backend.core.i18n import get_language_from_request
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import RegisterRequestSerializer


@extend_schema(tags=['Identity — Auth'])
class RegisterView(APIView):
    """Register a new user account."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_register',
        summary='Register a new user',
        description=(
            'Creates a new user account (inactive until email is verified). '
            'Sends a verification email asynchronously via Celery.'
        ),
        request=RegisterRequestSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Register Request',
                value={
                    'email': 'student@example.com',
                    'password': 'SecurePass123!',
                    'first_name': 'Alisher',
                    'last_name': 'Umarov',
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        lang = get_language_from_request(request)

        try:
            register_user(**serializer.validated_data, lang=lang)
        except AuthError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'detail': 'Registration successful. Please verify your email.'},
            status=status.HTTP_201_CREATED,
        )
