"""
GenerateCertificate Command — создание сертификата для студента.
"""

import secrets
import string
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from src.backend.certificates.domain.models import Certificate, CertificateTemplate
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.learning.domain.models import Course

User = get_user_model()


@dataclass
class GenerateCertificateData:
    """Input data для генерации сертификата."""
    user_id: str
    enrollment_id: Optional[str] = None
    course_id: Optional[str] = None
    template_id: Optional[str] = None
    final_score: Optional[Decimal] = None
    completion_date: Optional[date] = None
    metadata: Optional[dict] = None


def generate_certificate_number() -> str:
    """
    Генерирует уникальный номер сертификата.
    Формат: LF-YYYYMMDD-XXXXXX (например: LF-20260629-A3F8K2)
    """
    today = date.today().strftime('%Y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"LF-{today}-{random_part}"


def generate_verification_code() -> str:
    """
    Генерирует код верификации.
    Формат: VERIFY-XXXXXXXX (16 символов)
    """
    return f"VERIFY-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))}"


class GenerateCertificateHandler:
    """Handler для генерации сертификата."""

    @staticmethod
    @transaction.atomic
    def handle(data: GenerateCertificateData) -> Certificate:
        """
        Генерирует сертификат.

        Если указан enrollment_id — берёт данные из него.
        Если указан course_id — создаёт для курса напрямую.
        """
        
        try:
            user = User.objects.get(id=data.user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User {data.user_id} not found")

        
        enrollment = None
        course = None
        course_id = None
        student_name = ""
        course_name = ""
        course_description = ""
        final_score = data.final_score
        completion_date = data.completion_date or date.today()

        if data.enrollment_id:
            try:
                enrollment = CourseEnrollment.objects.get(id=data.enrollment_id)
                course_id = enrollment.course_id
            except CourseEnrollment.DoesNotExist:
                raise ValidationError(f"Enrollment {data.enrollment_id} not found")
        elif data.course_id:
            course_id = data.course_id
        else:
            raise ValidationError("Either enrollment_id or course_id must be provided")

        
        try:
            course = Course.objects.get(id=course_id, deleted_at__isnull=True)
        except Course.DoesNotExist:
            raise ValidationError(f"Course {course_id} not found")

        
        if hasattr(user, 'info') and user.info:
            first_name = user.info.first_name or ''
            last_name = user.info.last_name or ''
            student_name = f"{first_name} {last_name}".strip()

        if not student_name:
            student_name = user.email or str(user.id)

        
        course_name = course.title
        course_description = course.short_description or course.description or ""

        
        if final_score is None:
            final_score = Decimal('100.00')

        
        template = None
        if data.template_id:
            try:
                template = CertificateTemplate.objects.get(id=data.template_id, is_active=True)
            except CertificateTemplate.DoesNotExist:
                raise ValidationError(f"Template {data.template_id} not found or inactive")
        else:
            
            template = CertificateTemplate.objects.filter(is_active=True).first()

            
            if not template:
                template = CertificateTemplate.objects.create(
                    name="Default Certificate",
                    description="Standard course completion certificate",
                    is_active=True,
                )

        
        certificate_number = generate_certificate_number()
        verification_code = generate_verification_code()

        
        while Certificate.objects.filter(certificate_number=certificate_number).exists():
            certificate_number = generate_certificate_number()

        while Certificate.objects.filter(verification_code=verification_code).exists():
            verification_code = generate_verification_code()

        
        certificate = Certificate.objects.create(
            user=user,
            enrollment_id=enrollment.id if enrollment else None,
            course_id=course_id,
            certificate_number=certificate_number,
            verification_code=verification_code,
            student_full_name_snapshot=student_name,
            course_name_snapshot=course_name,
            course_description_snapshot=course_description,
            final_score=final_score,
            completion_date=completion_date,
            issued_at=timezone.now(),
            status='issued',  
            template_id=template.id,
            metadata=data.metadata or {},
        )

        return certificate