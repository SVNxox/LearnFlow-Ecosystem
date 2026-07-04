"""
Celery tasks for Certificates Domain
"""

import logging
from uuid import UUID

from celery import shared_task

from src.backend.certificates.domain.models.certificate import Certificate
from src.backend.certificates.domain.services.certificate_service import CertificateService
from src.backend.certificates.infrastructure.integrations.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  
)
def generate_certificate_pdf(self, certificate_id: str) -> None:
    """
    Generate PDF for a certificate (async).

    This task is triggered after certificate record is created.
    PDF generation can take 5-15 seconds.

    Flow:
    1. Fetch certificate from DB
    2. Generate PDF using template
    3. Upload PDF to S3
    4. Mark certificate as 'issued' with pdf_url
    """

    try:
        certificate = Certificate.objects.select_related('template').get(
            id=UUID(certificate_id)
        )

        if certificate.status != 'pending':
            logger.warning(
                f"Certificate {certificate_id} is not pending (status: {certificate.status})"
            )
            return

        logger.info(f"Generating PDF for certificate {certificate_id}")

        
        pdf_url = PDFGenerator.generate_certificate_pdf(
            certificate_id=certificate.id,
            template_path=certificate.template.pdf_template,
            background_image_url=certificate.template.background_image,
            student_name=certificate.student_full_name_snapshot,
            course_name=certificate.course_name_snapshot,
            course_description=certificate.course_description_snapshot,
            certificate_number=certificate.certificate_number,
            completion_date=certificate.completion_date.isoformat(),
            final_score=float(certificate.final_score) if certificate.final_score else None,
        )

        
        CertificateService.mark_as_issued(
            certificate_id=certificate.id,
            pdf_url=pdf_url,
        )

        logger.info(f"Certificate {certificate_id} PDF generated: {pdf_url}")

    except Certificate.DoesNotExist:
        logger.error(f"Certificate {certificate_id} not found")
        raise

    except Exception as e:
        logger.error(
            f"Error generating PDF for certificate {certificate_id}: {e}",
            exc_info=True
        )
        
        raise self.retry(exc=e)
