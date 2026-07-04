"""
Certificate Issued event
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CertificateIssuedEvent:
    """
    Certificate has been issued (PDF generated successfully).

    This is a critical event → Outbox Pattern.
    Triggers: Notifications (send email to student)
    """

    certificate_id: UUID
    user_id: UUID
    enrollment_id: UUID
    course_id: UUID
    certificate_number: str
    verification_code: str
    student_full_name: str
    course_name: str
    pdf_url: str
    issued_at: datetime
    occurred_at: datetime
