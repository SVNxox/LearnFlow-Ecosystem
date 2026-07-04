from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from src.backend.identity.models import (
    User, UserInfo, UserSettings, Role, UserRole,
    StudentProfile, MentorProfile, RefreshToken,
    LoginAttempt,
)


class UserInfoInline(admin.StackedInline):
    model = UserInfo
    extra = 0
    can_delete = False


class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    extra = 0
    can_delete = False


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    fk_name = "user"
    autocomplete_fields = ["role"]
    readonly_fields = ["assigned_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ["email", "is_active", "is_blocked", "is_staff", "created_at"]
    list_filter     = ["is_active", "is_blocked", "is_staff"]
    search_fields   = ["email"]
    ordering        = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login_at", "last_login_ip"]
    inlines         = [UserInfoInline, UserSettingsInline, UserRoleInline]

    fieldsets = (
        (None,          {"fields": ("id", "email", "password")}),
        ("Status",      {"fields": ("is_active", "is_blocked", "is_staff", "is_superuser")}),
        ("Lockout",     {"fields": ("failed_login_attempts", "locked_until")}),
        ("Last login",  {"fields": ("last_login_at", "last_login_ip")}),
        ("Timestamps",  {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    filter_horizontal = ()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ["name", "description", "created_at"]
    search_fields = ["name"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display  = ["user", "role", "is_active", "assigned_at", "assigned_by"]
    list_filter   = ["is_active", "role"]
    search_fields = ["user__email"]
    readonly_fields = ["assigned_at"]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "enrollment_date", "streak_days", "total_xp", "mentor"]
    search_fields = ["user__email"]
    raw_id_fields = ["user", "mentor"]


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "max_students", "current_student_count", "is_available", "rating"]
    list_filter   = ["is_available"]
    search_fields = ["user__email"]


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display  = ["user", "device_name", "ip_address", "created_at", "expires_at", "revoked_at"]
    list_filter   = ["revoked_at"]
    search_fields = ["user__email", "ip_address"]
    readonly_fields = ["token_hash", "created_at"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display  = ["email_used", "ip_address", "success", "failure_reason", "attempted_at"]
    list_filter   = ["success"]
    search_fields = ["email_used", "ip_address"]
    readonly_fields = ["attempted_at"]