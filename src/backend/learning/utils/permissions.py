from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    """
    Разрешает доступ только пользователям с ролями 'admin' или 'staff'.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            user_roles = request.user.get_roles()
            return 'admin' in user_roles or 'staff' in user_roles
        except (AttributeError, Exception):
            return False


class IsAdmin(BasePermission):
    """Разрешает доступ только пользователям с ролью 'admin'."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            user_roles = request.user.get_roles()
            return 'admin' in user_roles
        except (AttributeError, Exception):
            return False


from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()


def can_manage_course(actor: User, course) -> bool:
    """
    Проверяет, может ли пользователь управлять курсом.

    Разрешено:
    - admin
    - staff
    - course author

    Args:
        actor: Пользователь
        course: Объект курса

    Returns:
        bool: True если может управлять
    """
    if not actor or not actor.is_authenticated:
        return False

    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course.created_by_id == actor.id

    return is_admin or is_staff or is_course_author


def can_manage_module(actor: User, module) -> bool:
    """
    Проверяет, может ли пользователь управлять модулем.

    Разрешено:
    - admin
    - staff
    - course author (автор курса, которому принадлежит модуль)
    """
    if not actor or not actor.is_authenticated:
        return False

    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = module.course.created_by_id == actor.id

    return is_admin or is_staff or is_course_author


def can_manage_lesson(actor: User, lesson) -> bool:
    """
    Проверяет, может ли пользователь управлять уроком.

    Разрешено:
    - admin
    - staff
    - course author (автор курса, которому принадлежит урок)
    """
    if not actor or not actor.is_authenticated:
        return False

    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = lesson.module.course.created_by_id == actor.id

    return is_admin or is_staff or is_course_author


def can_view_all_content(actor: Optional[User], course=None) -> bool:
    """
    Проверяет, может ли пользователь видеть весь контент (включая drafts).

    Разрешено:
    - admin
    - staff
    - course author (если передан course)
    """
    if not actor or not actor.is_authenticated:
        return False

    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course and course.created_by_id == actor.id

    return is_admin or is_staff or bool(is_course_author)