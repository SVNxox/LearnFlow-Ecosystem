"""
identity/presentation/rest/v1/profile/settings.py

GET /api/v1/identity/profile/me/settings/
PATCH /api/v1/identity/profile/me/settings/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSettingsSerializer


@extend_schema(tags=['Identity — Settings'])
class UserSettingsView(APIView):
    """User notification and UI preferences."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_settings_retrieve',
        summary='Get user settings',
        responses={200: UserSettingsSerializer},
    )
    def get(self, request):
        serializer = UserSettingsSerializer(request.user.settings)
        return Response(serializer.data)

    @extend_schema(
        operation_id='identity_settings_update',
        summary='Update user settings',
        request=UserSettingsSerializer,
        responses={200: UserSettingsSerializer},
    )
    def patch(self, request):
        settings_obj = request.user.settings
        serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
