from rest_framework import serializers
from src.backend.identity.models import User, UserInfo, Role, UserRole


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'phone', 'avatar_url']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer для списка пользователей (админ-панель)."""
    info = UserInfoSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    is_locked = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'is_active', 'is_blocked', 'is_locked',
            'locked_until', 'created_at', 'last_login_at', 'info', 'roles'
        ]

    def get_roles(self, obj):
        return obj.get_roles()


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer для детальной информации о пользователе."""
    info = UserInfoSerializer(required=False)
    roles = serializers.SerializerMethodField()
    is_locked = serializers.ReadOnlyField()

    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'is_active', 'is_blocked', 'is_locked',
            'locked_until', 'created_at', 'last_login_at', 'last_login_ip',
            'failed_login_attempts', 'info', 'roles',
            'first_name', 'last_name', 'phone', 'bio',
        ]
        read_only_fields = ['id', 'created_at', 'last_login_at', 'last_login_ip', 'failed_login_attempts']

    def get_roles(self, obj):
        return obj.get_roles()

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        phone = validated_data.pop('phone', None)
        bio = validated_data.pop('bio', None)

        info_data = validated_data.pop('info', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        from src.backend.identity.models import UserInfo
        info, _ = UserInfo.objects.get_or_create(user=instance)

        if first_name is not None:
            info.first_name = first_name
        if last_name is not None:
            info.last_name = last_name
        if phone is not None:
            info.phone = phone
        if bio is not None:
            info.bio = bio

        for attr, value in info_data.items():
            if hasattr(info, attr):
                setattr(info, attr, value)

        info.save()

        return instance


import logging

logger = logging.getLogger(__name__)


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания пользователя (админ-панель)."""

    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False)

    role = serializers.CharField(write_only=True, required=False)
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    password = serializers.CharField(write_only=True, min_length=8)

    info = UserInfoSerializer(read_only=True)
    roles_list = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'password', 'is_active', 'is_blocked',
            'first_name', 'last_name', 'phone', 'bio',
            'role', 'roles',
            'info', 'roles_list',
        ]

    def get_roles_list(self, obj):
        return obj.get_roles()

    def create(self, validated_data):
        
        logger.info("UserCreateSerializer.create() called with: %s", validated_data)

        
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        phone = validated_data.pop('phone', '')
        bio = validated_data.pop('bio', '')

        logger.info("Extracted fields: first_name=%s, last_name=%s, phone=%s, bio=%s",
                    first_name, last_name, phone, bio)

        
        role_name = validated_data.pop('role', None)
        roles_data = validated_data.pop('roles', [])

        if role_name and not roles_data:
            roles_data = [role_name]

        logger.info("Roles to assign: %s", roles_data)

        password = validated_data.pop('password')

        
        email = validated_data['email'].strip().lower()

        
        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=validated_data.get('is_active', True),
        )

        logger.info("User created with ID: %s", user.id)

        
        if 'is_blocked' in validated_data:
            user.is_blocked = validated_data['is_blocked']
            user.save(update_fields=['is_blocked'])

        
        from src.backend.identity.models import UserInfo
        info, created = UserInfo.objects.get_or_create(user=user)

        logger.info("UserInfo %s for user %s",
                    'created' if created else 'already exists', user.id)

        if first_name:
            info.first_name = first_name
        if last_name:
            info.last_name = last_name
        if phone:
            info.phone = phone
        if bio:
            info.bio = bio

        info.save()

        logger.info("UserInfo saved: first_name=%s, last_name=%s",
                    info.first_name, info.last_name)

        
        if roles_data:
            from src.backend.identity.models import Role, UserRole
            for role_name in roles_data:
                role, _ = Role.objects.get_or_create(name=role_name)
                UserRole.objects.create(user=user, role=role)
                logger.info("Role '%s' assigned to user %s", role_name, user.id)

        logger.info("User creation completed for %s", user.email)

        return user


class UserUpdateRolesSerializer(serializers.Serializer):
    """Serializer для обновления ролей пользователя."""
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )

    def validate_roles(self, value):
        if not value:
            raise serializers.ValidationError("Роли не могут быть пустыми")
        return value