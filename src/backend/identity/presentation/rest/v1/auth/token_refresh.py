"""
identity/presentation/rest/v1/auth/token_refresh.py

POST /api/v1/identity/auth/token/refresh/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.i18n import get_language_from_request
from src.backend.identity.services import refresh_access_token, AuthError
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import TokenRefreshRequestSerializer, TokenResponseSerializer


@extend_schema(tags=['Identity — Auth'])
class TokenRefreshView(APIView):
    """Refresh access token using a valid refresh token."""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='identity_auth_token_refresh',
        summary='Refresh access token',
        description='Exchange a valid refresh token for a new access token + rotated refresh token.',
        request=TokenRefreshRequestSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Refresh request data: {request.data}")
        logger.info(f"Refresh request headers: {dict(request.headers)}")

        serializer = TokenRefreshRequestSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Refresh validation errors: {serializer.errors}")

        serializer.is_valid(raise_exception=True)

        lang = get_language_from_request(request.headers.get('Accept-Language', 'uz'))

        result = refresh_access_token(
            raw_refresh=serializer.validated_data['refresh_token'],
            request=request,
            lang=lang,
        )

        logger.info(f"Refresh result keys: {result.keys()}")

        response_serializer = TokenResponseSerializer(result)
        logger.info(f"Refresh response data: {response_serializer.data}")

        return Response(response_serializer.data, status=status.HTTP_200_OK)