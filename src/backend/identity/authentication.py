"""
Custom DRF authentication backend.
Validates Bearer JWT access token on every request.
Caches user lookup to reduce DB hits.
"""
import logging

from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from src.backend.identity.models import User
from src.backend.identity.tokens import JWTService

logger = logging.getLogger(__name__)

CACHE_TTL = 60


class JWTAuthentication(BaseAuthentication):
    """
    Authenticate via Authorization: Bearer <access_token> header.
    """
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None

        raw_token = header[len("Bearer "):]

        try:
            payload = JWTService.decode_access_token(raw_token)
        except ValueError as exc:
            raise AuthenticationFailed(str(exc))

        if payload.get("type") != "access":
            raise AuthenticationFailed("Invalid token type.")

        user_id = payload.get("sub")
        user = self._get_user(user_id)

        if not user:
            raise AuthenticationFailed("User not found.")
        if not user.is_active:
            raise AuthenticationFailed("Account is inactive.")
        if user.is_blocked:
            raise AuthenticationFailed("Account is suspended.")

        return user, payload

    @staticmethod
    def _get_user(user_id: str):
        cache_key = f"user:{user_id}:state"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            user = (
                User.objects
                .select_related("info", "settings")
                .prefetch_related("user_roles__role")
                .get(id=user_id)
            )
        except User.DoesNotExist:
            return None

        cache.set(cache_key, user, timeout=CACHE_TTL)
        return user

    def authenticate_header(self, request):
        return "Bearer"