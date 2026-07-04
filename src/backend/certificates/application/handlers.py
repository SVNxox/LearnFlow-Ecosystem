"""
Event handler for CourseCompleted event from Progress Domain
"""

import logging
from datetime import date
from decimal import Decimal

from src.backend.certificates.application.commands.generate_certificate import (
    GenerateCertificateCommand,
    GenerateCertificateHandler,
)

logger = logging.getLogger(__name__)


def handle_course_completed(payload: dict) -> None:
    """
    Handle CourseCompleted event from Progress Domain.

    Generates a certificate for the student who completed the course.

    Event payload:
    {
        'enrollment_id': UUID,
        'user_id': UUID,
        'course_id': UUID,
        'student_full_name': str,
        'course_name': str,
        'course_description': str,
        'template_id': UUID,
        'final_score': Decimal,
        'completion_date': date,
    }
    """

    try:
        command = GenerateCertificateCommand(
            user_id=payload['user_id'],
            enrollment_id=payload['enrollment_id'],
            course_id=payload['course_id'],
            template_id=payload['template_id'],
            student_full_name=payload['student_full_name'],
            course_name=payload['course_name'],
            course_description=payload.get('course_description'),
            final_score=Decimal(str(payload['final_score'])) if payload.get('final_score') else None,
            completion_date=date.fromisoformat(payload['completion_date']),
        )

        handler = GenerateCertificateHandler()
        certificate = handler.handle(command)

        logger.info(
            f"Certificate {certificate.id} generated for enrollment {payload['enrollment_id']}"
        )

    except Exception as e:
        logger.error(
            f"Error handling CourseCompleted event for enrollment {payload.get('enrollment_id')}: {e}",
            exc_info=True
        )
        raise
