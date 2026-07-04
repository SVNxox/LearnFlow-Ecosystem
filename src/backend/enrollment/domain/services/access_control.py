"""
AccessControlService — Domain Service for checking content access.
"""

from datetime import timedelta
from typing import Tuple
from uuid import UUID

from django.contrib.auth import get_user_model
from django.utils import timezone

from src.backend.enrollment.domain.models import CourseEnrollment, AccessRule

User = get_user_model()


class AccessControlService:
    """
    Domain service for access control checks.

    Responsibilities:
    - Check if student can access specific content
    - Evaluate access rules (time-based, prerequisites, payment, delivery format)
    """

    @staticmethod
    def can_access_content(
        user: User,
        course_id: UUID,
        content_id: UUID
    ) -> Tuple[bool, str]:
        """
        Check if student has access to specific content.

        Checks:
        1. Active enrollment
        2. Basic access (can_access_course)
        3. Content-specific rules

        Args:
            user: User requesting access
            course_id: Course UUID
            content_id: Content UUID (lesson, module, or content item)

        Returns:
            (can_access, reason)
            - can_access: True if access granted
            - reason: Empty string if granted, error message if denied
        """
        
        try:
            enrollment = CourseEnrollment.objects.select_related('user').get(
                user=user,
                course_id=course_id,
                deleted_at__isnull=True
            )
        except CourseEnrollment.DoesNotExist:
            return False, "Not enrolled in course"

        
        if not enrollment.can_access_course():
            if enrollment.status != CourseEnrollment.Status.ACTIVE:
                return False, f"Enrollment status is {enrollment.status}"
            if enrollment.is_expired():
                return False, "Enrollment has expired"
            return False, "Access denied"

        
        rules = AccessRule.objects.filter(
            enrollment=enrollment,
            resource_id=content_id,
            is_active=True
        )

        for rule in rules:
            can_access, reason = AccessControlService._check_rule(enrollment, rule)
            if not can_access:
                return False, reason

        return True, ""

    @staticmethod
    def _check_rule(enrollment: CourseEnrollment, rule: AccessRule) -> Tuple[bool, str]:
        """
        Check specific access rule.

        Rule types:
        - time_based: Available after X days from enrollment
        - prerequisite: Requires completion of another resource
        - payment_tier: Requires specific payment status
        - delivery_format: Restricted by delivery format
        """
        if rule.rule_type == AccessRule.RuleType.TIME_BASED:
            days_after = rule.rule_config.get('days_after_enrollment', 0)
            unlock_date = enrollment.enrolled_at + timedelta(days=days_after)

            if timezone.now() < unlock_date:
                return False, f"Content unlocks on {unlock_date.date()}"

        elif rule.rule_type == AccessRule.RuleType.PAYMENT_TIER:
            required_status = rule.rule_config.get('required_payment_status')

            if enrollment.payment_status != required_status:
                return False, "Requires paid access"

        elif rule.rule_type == AccessRule.RuleType.DELIVERY_FORMAT:
            allowed_formats = rule.rule_config.get('allowed_formats', [])

            if enrollment.delivery_format not in allowed_formats:
                return False, f"Content only available for {', '.join(allowed_formats)} students"

        elif rule.rule_type == AccessRule.RuleType.PREREQUISITE:
            
            
            
            pass

        return True, ""
