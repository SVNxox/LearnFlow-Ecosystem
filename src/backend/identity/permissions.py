"""
Custom DRF permissions based on the role system.
"""
from rest_framework.permissions import BasePermission
from src.backend.identity.models import Role, User


class BaseRolePermission(BasePermission):
    """
    Base class for role-based checks.
    Subclasses must specify required_roles and message.
    """
    required_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(request, "auth") and isinstance(request.auth, dict):
            token_roles = request.auth.get("roles", [])
            return bool(set(self.required_roles) & set(token_roles))

        return request.user.has_any_role(self.required_roles)


class IsAdmin(BaseRolePermission):
    """Allow access only to users with the 'admin' role."""
    required_roles = [Role.ADMIN]
    message = "Admin huquqi talab qilinadi."


class IsMentor(BaseRolePermission):
    """Allow access to users with 'mentor' or 'admin' roles."""
    required_roles = [Role.MENTOR, Role.ADMIN]
    message = "Mentor huquqi talab qilinadi."


class IsStaff(BaseRolePermission):
    """Allow access to users with 'staff' or 'admin' roles."""
    required_roles = [Role.STAFF, Role.ADMIN]
    message = "Xodimlar huquqi talab qilinadi."


class IsStudent(BaseRolePermission):
    """Allow access to users with the 'student' role."""
    required_roles = [Role.STUDENT]
    message = "Talaba huquqi talab qilinadi."


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow if user owns the object or is admin.
    """
    message = "Sizda ushbu resursdan foydalanish huquqi yo‘q."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.has_role(Role.ADMIN):
            return True

        obj_user_id = getattr(obj, "user_id", None)

        if obj_user_id is None and isinstance(obj, User):
            obj_user_id = obj.id

        if obj_user_id is None:
            return False

        return str(obj_user_id) == str(request.user.id)