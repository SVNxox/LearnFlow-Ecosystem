"""
Certificate domain events
"""

from .certificate_issued import CertificateIssuedEvent
from .certificate_revoked import CertificateRevokedEvent

__all__ = [
    'CertificateIssuedEvent',
    'CertificateRevokedEvent',
]
