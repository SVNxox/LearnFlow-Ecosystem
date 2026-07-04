"""
identity/presentation/rest/v1/profile/change_password.py

POST /api/v1/identity/profile/me/password/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.services import change_password, AuthError
from src.backend.shared.presentation.serializers import ErrorResponseSerializer
from .serializers import ChangePasswordSerializer


@extend_schema(tags=['Identity — Profile'])
class ChangePasswordView(APIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_profile_change_password',
        summary='Change password',
        description='Requires current password. Revokes all sessions after success.',
        request=ChangePasswordSerializer,
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
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password'],
            )
        except AuthError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'detail': 'Password changed. Please log in again.'})
