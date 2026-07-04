from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.identity.models import User, RefreshToken
from src.backend.identity.permissions import IsAdmin
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
)


@extend_schema(tags=['Identity — Admin'])
class UserListView(generics.ListCreateAPIView):
    """
    GET /api/v1/identity/admin/users/ - Список пользователей
    POST /api/v1/identity/admin/users/ - Создание пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        queryset = User.objects.select_related('info').prefetch_related('user_roles__role')

        
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(info__first_name__icontains=search) |
                Q(info__last_name__icontains=search)
            )

        
        role = self.request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(user_roles__role__name=role)

        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        is_blocked = self.request.query_params.get('is_blocked')
        if is_blocked is not None:
            queryset = queryset.filter(is_blocked=is_blocked.lower() == 'true')

        return queryset.order_by('-created_at')


@extend_schema(tags=['Identity — Admin'])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/identity/admin/users/{id}/ - Детали пользователя
    PUT/PATCH /api/v1/identity/admin/users/{id}/ - Обновление пользователя
    DELETE /api/v1/identity/admin/users/{id}/ - Удаление пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserDetailSerializer
    queryset = User.objects.select_related('info').prefetch_related('user_roles__role')
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def perform_destroy(self, instance):
        
        instance.is_active = False
        instance.is_blocked = True
        instance.save()


@extend_schema(tags=['Identity — Admin'])
class UserChangeRoleView(APIView):
    """
    POST /api/v1/identity/admin/users/{id}/change-role/ - Изменение роли пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'role': {'type': 'string'}
            },
            'required': ['role']
        },
        responses={200: UserDetailSerializer},
    )
    def post(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        role_name = request.data.get('role')
        if not role_name:
            return Response(
                {'detail': 'Role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        user.user_roles.all().delete()

        
        from src.backend.identity.models import Role, UserRole
        role, _ = Role.objects.get_or_create(name=role_name)
        UserRole.objects.create(user=user, role=role)

        
        user_serializer = UserDetailSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Identity — Admin'])
class UserBlockView(APIView):
    """
    POST /api/v1/identity/admin/users/{id}/block/ - Блокировка пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'reason': {'type': 'string'}
            }
        },
        responses={200: UserDetailSerializer},
    )
    def post(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_blocked = True
        user.save(update_fields=['is_blocked'])

        user_serializer = UserDetailSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Identity — Admin'])
class UserUnblockView(APIView):
    """
    POST /api/v1/identity/admin/users/{id}/unblock/ - Разблокировка пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(responses={200: UserDetailSerializer})
    def post(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_blocked = False
        user.save(update_fields=['is_blocked'])

        user_serializer = UserDetailSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Identity — Admin'])
class UserSessionsView(APIView):
    """
    GET /api/v1/identity/admin/users/{id}/sessions/ - Список активных сессий пользователя
    DELETE /api/v1/identity/admin/users/{id}/sessions/ - Отзыв всех сессий пользователя
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={200: {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'device_name': {'type': 'string'},
                    'ip_address': {'type': 'string'},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'expires_at': {'type': 'string', 'format': 'date-time'},
                }
            }
        }}
    )
    def get(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        
        sessions = RefreshToken.objects.filter(
            user=user,
            revoked_at__isnull=True
        ).values('id', 'device_name', 'ip_address', 'created_at', 'expires_at')

        return Response(list(sessions), status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        
        count = RefreshToken.objects.filter(
            user=user,
            revoked_at__isnull=True
        ).update(revoked_at=timezone.now())

        return Response(
            {'detail': f'{count} sessions revoked'},
            status=status.HTTP_200_OK
        )