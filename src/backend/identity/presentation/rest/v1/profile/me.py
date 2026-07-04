"""
identity/presentation/rest/v1/profile/me.py

GET /api/v1/identity/profile/me/
PATCH /api/v1/identity/profile/me/
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserProfileSerializer, UserProfileUpdateSerializer


@extend_schema(tags=['Identity — Profile'])
class MeView(APIView):
    """Current user profile endpoint."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='identity_profile_me_retrieve',
        summary='Get current user profile',
        description='Returns full profile: identity, info, settings, and active roles.',
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        operation_id='identity_profile_me_update',
        summary='Update profile info',
        description='Partially updates UserInfo fields (first_name, last_name, phone, bio, date_of_birth).',
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer},
    )
    def patch(self, request):
        user_info = request.user.info
        serializer = UserProfileUpdateSerializer(user_info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)
