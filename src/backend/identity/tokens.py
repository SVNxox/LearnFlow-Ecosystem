"""
JWT access token creation and verification using RS256.
No dependency on djangorestframework-simplejwt — pure PyJWT.
"""
import logging
from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


class JWTService:
    ALGORITHM = "RS256"
    ACCESS_LIFETIME = timedelta(hours=2)  
    REFRESH_LIFETIME = timedelta(days=7)

    @classmethod
    def _has_rsa_keys(cls) -> bool:
        """Check if RSA keys are configured."""
        return bool(
            getattr(settings, "JWT_PRIVATE_KEY", None)
            and getattr(settings, "JWT_PUBLIC_KEY", None)
        )

    @classmethod
    def _algorithm(cls) -> str:
        """Determine algorithm based on available keys."""
        return cls.ALGORITHM if cls._has_rsa_keys() else "HS256"

    @classmethod
    def _signing_key(cls):
        """Get key for signing (private key for RS256, secret for HS256)."""
        if cls._has_rsa_keys():
            return settings.JWT_PRIVATE_KEY
        return settings.SECRET_KEY

    @classmethod
    def _verifying_key(cls):
        """Get key for verification (public key for RS256, secret for HS256)."""
        if cls._has_rsa_keys():
            return settings.JWT_PUBLIC_KEY
        return settings.SECRET_KEY

    @classmethod
    def create_access_token(cls, user) -> str:
        now = timezone.now()
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": user.get_roles(),
            "iat": int(now.timestamp()),
            "exp": int((now + cls.ACCESS_LIFETIME).timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, cls._signing_key(), algorithm=cls._algorithm())

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        try:
            
            logger.debug(f"Decoding token: {token[:50]}...")

            return jwt.decode(
                token,
                cls._verifying_key(),
                algorithms=[cls._algorithm()],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as exc:
            
            logger.error(f"Invalid token error: {exc}")
            logger.error(f"Token: {token[:100]}...")
            logger.error(f"Algorithm: {cls._algorithm()}")
            logger.error(f"Has RSA keys: {cls._has_rsa_keys()}")
            raise ValueError(f"Invalid token: {exc}")