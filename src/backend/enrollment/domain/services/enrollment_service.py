"""
EnrollmentService — Core Domain Service for enrollment operations.
"""

from typing import Tuple
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services.prerequisite_checker import PrerequisiteChecker
from src.backend.enrollment.domain.events import StudentEnrolledEvent
from src.backend.shared.infrastructure.outbox.publisher import publish_to_outbox

User = get_user_model()


class EnrollmentService:
    """
    Core domain service for enrollment business logic.

    Responsibilities:
    - Validate enrollment rules
    - Create enrollments
    - Publish critical events
    """

    @staticmethod
    def can_student_enroll(user: User, course_id: UUID) -> Tuple[bool, str]:
        """
        Check all enrollment business rules.

        BR-01: Student cannot enroll twice in same course
        BR-02: Course must be published (checked by caller)
        BR-03: Course must not be full (checked by caller)
        BR-04: Student must meet prerequisites

        Returns:
            (can_enroll, reason)
        """
        
        if CourseEnrollment.objects.filter(
            user=user,
            course_id=course_id,
            status__in=[
                CourseEnrollment.Status.PENDING,
                CourseEnrollment.Status.ACTIVE,
                CourseEnrollment.Status.SUSPENDED
            ],
            deleted_at__isnull=True
        ).exists():
            return False, "Already enrolled in this course"

        
        has_prereqs, missing = PrerequisiteChecker.check(user, course_id)
        if not has_prereqs:
            return False, f"Missing prerequisites: {', '.join(missing)}"

        return True, ""

    @staticmethod
    @transaction.atomic
    def enroll_student(
        user: User,
        course_id: UUID,
        delivery_format: str,
        payment_id: UUID = None,
        enrolled_by: User = None,
        access_level: str = CourseEnrollment.AccessLevel.FULL
    ) -> CourseEnrollment:
        """
        Core enrollment logic.

        Creates enrollment and publishes StudentEnrolled event (Outbox).

        Args:
            user: Student to enroll
            course_id: Course UUID
            delivery_format: online/offline/hybrid
            payment_id: Payment UUID (if paid course)
            enrolled_by: User who created enrollment (None = self-enrolled)
            access_level: full/limited/preview

        Returns:
            CourseEnrollment

        Raises:
            ValidationError: If enrollment rules violated
        """
        
        can_enroll, reason = EnrollmentService.can_student_enroll(user, course_id)
        if not can_enroll:
            raise ValidationError(reason)

        
        if payment_id:
            initial_status = CourseEnrollment.Status.PENDING
            payment_status = CourseEnrollment.PaymentStatus.PENDING
        else:
            
            initial_status = CourseEnrollment.Status.ACTIVE
            payment_status = CourseEnrollment.PaymentStatus.PAID

        
        enrollment = CourseEnrollment.objects.create(
            user=user,
            course_id=course_id,
            delivery_format=delivery_format,
            access_level=access_level,
            status=initial_status,
            payment_id=payment_id,
            payment_status=payment_status,
            enrolled_by=enrolled_by or user,
        )

        
        event = StudentEnrolledEvent(
            enrollment_id=enrollment.id,
            user_id=user.id,
            course_id=course_id,
            delivery_format=delivery_format,
            status=enrollment.status,
            occurred_at=timezone.now()
        )

        transaction.on_commit(
            lambda: publish_to_outbox(
                event_type='StudentEnrolled',
                aggregate_id=enrollment.id,
                payload=event.to_dict()
            )
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def activate_enrollment(enrollment_id: UUID, payment_id: UUID) -> CourseEnrollment:
        """
        Activate enrollment after successful payment.

        Called by Payment Domain when payment succeeds.
        """
        enrollment = CourseEnrollment.objects.select_for_update().get(
            id=enrollment_id
        )

        if enrollment.status != CourseEnrollment.Status.PENDING:
            raise ValidationError(f"Cannot activate enrollment with status {enrollment.status}")

        enrollment.status = CourseEnrollment.Status.ACTIVE
        enrollment.payment_status = CourseEnrollment.PaymentStatus.PAID
        enrollment.payment_id = payment_id
        enrollment.save(update_fields=['status', 'payment_status', 'payment_id', 'updated_at'])

        
        from src.backend.enrollment.domain.events import access_granted
        transaction.on_commit(
            lambda: access_granted.send(
                sender=CourseEnrollment,
                enrollment_id=enrollment.id,
                course_id=enrollment.course_id,
                user_id=enrollment.user_id
            )
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def suspend_enrollment(enrollment_id: UUID, reason: str) -> CourseEnrollment:
        """
        Suspend enrollment (payment failed or admin action).

        Called by Payment Domain when payment fails.
        """
        enrollment = CourseEnrollment.objects.select_for_update().get(
            id=enrollment_id
        )

        if enrollment.status not in [CourseEnrollment.Status.PENDING, CourseEnrollment.Status.ACTIVE]:
            raise ValidationError(f"Cannot suspend enrollment with status {enrollment.status}")

        enrollment.status = CourseEnrollment.Status.SUSPENDED
        enrollment.suspended_at = timezone.now()
        enrollment.suspended_reason = reason
        enrollment.save(update_fields=[
            'status', 'suspended_at', 'suspended_reason', 'updated_at'
        ])

        
        from src.backend.enrollment.domain.events import enrollment_suspended, access_revoked
        transaction.on_commit(
            lambda: [
                enrollment_suspended.send(
                    sender=CourseEnrollment,
                    enrollment_id=enrollment.id,
                    reason=reason
                ),
                access_revoked.send(
                    sender=CourseEnrollment,
                    enrollment_id=enrollment.id,
                    course_id=enrollment.course_id,
                    user_id=enrollment.user_id,
                    reason=reason
                )
            ]
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def drop_enrollment(enrollment_id: UUID, reason: str) -> CourseEnrollment:
        """
        Drop enrollment (student action or refund).

        Terminal state — cannot undo.
        """
        enrollment = CourseEnrollment.objects.select_for_update().get(
            id=enrollment_id
        )

        if enrollment.is_terminal_status():
            raise ValidationError(f"Enrollment already in terminal status {enrollment.status}")

        enrollment.status = CourseEnrollment.Status.DROPPED
        enrollment.dropped_at = timezone.now()
        enrollment.dropped_reason = reason
        enrollment.save(update_fields=[
            'status', 'dropped_at', 'dropped_reason', 'updated_at'
        ])

        
        from src.backend.enrollment.domain.events import enrollment_dropped
        transaction.on_commit(
            lambda: enrollment_dropped.send(
                sender=CourseEnrollment,
                enrollment_id=enrollment.id,
                reason=reason
            )
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def complete_enrollment(enrollment_id: UUID) -> CourseEnrollment:
        """
        Mark enrollment as completed.

        Called by Progress Domain when course is completed.
        """
        enrollment = CourseEnrollment.objects.select_for_update().get(
            id=enrollment_id
        )

        if enrollment.status != CourseEnrollment.Status.ACTIVE:
            raise ValidationError(f"Cannot complete enrollment with status {enrollment.status}")

        enrollment.status = CourseEnrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['status', 'completed_at', 'updated_at'])

        
        from src.backend.enrollment.domain.events import enrollment_completed
        transaction.on_commit(
            lambda: enrollment_completed.send(
                sender=CourseEnrollment,
                enrollment_id=enrollment.id
            )
        )

        return enrollment
