"""
Certificate Revoked event
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CertificateRevokedEvent:
    """
    Certificate has been revoked by admin.

    This is a critical event → Outbox Pattern.
    Triggers: Notifications (inform student), Analytics
    """

    certificate_id: UUID
    user_id: UUID
    certificate_number: str
    revoked_by_id: UUID
    revoked_reason: str
    revoked_at: datetime
    occurred_at: datetime
