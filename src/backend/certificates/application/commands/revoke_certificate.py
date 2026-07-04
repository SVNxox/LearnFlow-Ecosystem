"""
Revoke Certificate Command
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.certificates.domain.services.certificate_service import CertificateService
from src.backend.certificates.domain.models.certificate import Certificate


@dataclass
class RevokeCertificateCommand:
    """Command to revoke a certificate."""

    certificate_id: UUID
    revoked_by_id: UUID
    reason: str


class RevokeCertificateHandler:
    """Handler for RevokeCertificateCommand."""

    def handle(self, command: RevokeCertificateCommand) -> Certificate:
        """Revoke a certificate."""

        return CertificateService.revoke_certificate(
            certificate_id=command.certificate_id,
            revoked_by_id=command.revoked_by_id,
            reason=command.reason,
        )
