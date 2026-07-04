"""
Verify Certificate Query
"""

from dataclasses import dataclass
from typing import Optional

from src.backend.certificates.domain.services.verification_service import VerificationService


@dataclass
class VerifyCertificateQuery:
    """Query to verify a certificate by verification code."""

    verification_code: str


class VerifyCertificateQueryHandler:
    """Handler for VerifyCertificateQuery."""

    def handle(self, query: VerifyCertificateQuery) -> Optional[dict]:
        """
        Verify a certificate by its verification code.

        Returns certificate details if valid, None if not found.
        """

        return VerificationService.verify_by_code(query.verification_code)
