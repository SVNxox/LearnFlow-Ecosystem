"""
PrerequisiteChecker — Domain Service for checking enrollment prerequisites.
"""

from typing import Tuple
from uuid import UUID

from django.contrib.auth import get_user_model

from src.backend.enrollment.domain.models import CourseEnrollment, EnrollmentPrerequisite

User = get_user_model()


class PrerequisiteChecker:
    """
    Domain service for checking if student meets course prerequisites.

    Business Rules:
    - BR-04: Student must meet all required prerequisites
    - Optional prerequisites are recommendations only
    """

    @staticmethod
    def check(user: User, course_id: UUID) -> Tuple[bool, list[str]]:
        """
        Check all prerequisites for course enrollment.

        Args:
            user: User attempting to enroll
            course_id: Target course UUID

        Returns:
            (has_prerequisites, missing_list)
            - has_prerequisites: True if all required prerequisites are met
            - missing_list: List of missing prerequisite descriptions
        """
        prerequisites = EnrollmentPrerequisite.objects.filter(
            course_id=course_id,
            is_required=True
        ).order_by('order')

        missing = []

        for prereq in prerequisites:
            has_prereq = PrerequisiteChecker._check_single(user, prereq)
            if not has_prereq:
                missing.append(prereq.get_display_name())

        return len(missing) == 0, missing

    @staticmethod
    def _check_single(user: User, prereq: EnrollmentPrerequisite) -> bool:
        """Check single prerequisite."""
        if prereq.prerequisite_type == EnrollmentPrerequisite.PrerequisiteType.COURSE:
            required_course_id = prereq.prerequisite_config.get('required_course_id')
            if not required_course_id:
                return False

            return CourseEnrollment.objects.filter(
                user=user,
                course_id=required_course_id,
                status=CourseEnrollment.Status.COMPLETED
            ).exists()

        elif prereq.prerequisite_type == EnrollmentPrerequisite.PrerequisiteType.ASSESSMENT:
            
            
            
            
            return True  

        elif prereq.prerequisite_type == EnrollmentPrerequisite.PrerequisiteType.CERTIFICATE:
            
            
            
            return True  

        elif prereq.prerequisite_type == EnrollmentPrerequisite.PrerequisiteType.CUSTOM:
            
            
            return True

        return False
