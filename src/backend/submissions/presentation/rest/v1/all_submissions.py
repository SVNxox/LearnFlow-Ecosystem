"""
All Submissions API — получение всех submissions для менторов/стаффа/админов.
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.submissions.domain.models import Submission, Assignment, SubmissionRevision, SubmissionReview
from src.backend.identity.models import User, UserRole, Role
from src.backend.learning.domain.models import Lesson, Module, Course
from src.backend.enrollment.domain.models import CourseEnrollment

logger = logging.getLogger(__name__)


def is_mentor(user) -> bool:
    """Проверяет является ли пользователь ментором."""
    return UserRole.objects.filter(
        user=user,
        role__name=Role.MENTOR
    ).exists()


def can_view_all_submissions(user) -> bool:
    """Проверяет может ли пользователь просматривать все submissions."""
    if not user.is_authenticated:
        return False

    user_roles = user.get_roles() if hasattr(user, 'get_roles') else []

    return (
            'admin' in user_roles or
            'staff' in user_roles or
            is_mentor(user)
    )


class AllSubmissionsView(APIView):
    """Получить все submissions для менторов/стаффа/админов."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Получить список всех submissions с фильтрацией."""
        user = request.user

        if not can_view_all_submissions(user):
            return Response(
                {"detail": "You don't have permission to view all submissions."},
                status=status.HTTP_403_FORBIDDEN
            )

        
        queryset = Submission.objects.all().order_by('-created_at')

        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        
        course_id = request.query_params.get('course_id')
        if course_id:
            
            lesson_ids = Lesson.objects.filter(module__course_id=course_id).values_list('id', flat=True)
            queryset = queryset.filter(assignment__lesson_id__in=lesson_ids)

        
        lesson_id = request.query_params.get('lesson_id')
        if lesson_id:
            queryset = queryset.filter(assignment__lesson_id=lesson_id)

        
        student_id = request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        
        assignment_type = request.query_params.get('assignment_type')
        if assignment_type:
            queryset = queryset.filter(assignment__type=assignment_type)

        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        offset = (page - 1) * page_size

        total_count = queryset.count()
        submissions = queryset[offset:offset + page_size]

        
        data = []
        for submission in submissions:
            
            try:
                assignment = Assignment.objects.get(id=submission.assignment_id)
            except Assignment.DoesNotExist:
                continue

            
            lesson_info = None
            module_info = None
            course_info = None

            if assignment.lesson_id:
                try:
                    lesson = Lesson.objects.get(id=assignment.lesson_id)
                    lesson_info = {
                        "id": str(lesson.id),
                        "title": lesson.title,
                    }

                    module_info = {
                        "id": str(lesson.module_id),
                        "title": lesson.module.title,
                    }

                    course_info = {
                        "id": str(lesson.module.course_id),
                        "title": lesson.module.course.title,
                        "slug": lesson.module.course.slug,
                    }
                except (Lesson.DoesNotExist, Exception) as e:
                    logger.warning(f"Error loading lesson info: {e}")

            
            student_info = None
            try:
                student = User.objects.select_related('info').get(id=submission.student_id)
                student_info = {
                    "id": str(student.id),
                    "email": student.email,
                    "first_name": student.info.first_name if student.info else '',
                    "last_name": student.info.last_name if student.info else '',
                }
            except User.DoesNotExist:
                student_info = {
                    "id": str(submission.student_id),
                    "email": "Unknown",
                    "first_name": "Unknown",
                    "last_name": "",
                }

            data.append({
                "id": str(submission.id),
                "status": submission.status,
                "final_score": str(submission.final_score) if submission.final_score else None,
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "first_submitted_at": submission.first_submitted_at.isoformat() if submission.first_submitted_at else None,
                "last_submitted_at": submission.last_submitted_at.isoformat() if submission.last_submitted_at else None,
                "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                "deadline": submission.deadline.isoformat() if submission.deadline else None,

                
                "assignment": {
                    "id": str(assignment.id),
                    "title": assignment.title,
                    "type": assignment.type,
                    "max_score": str(assignment.max_score),
                },

                
                "lesson": lesson_info,
                "module": module_info,
                "course": course_info,

                
                "student": student_info,
            })

        return Response({
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "results": data,
        }, status=status.HTTP_200_OK)


class AllSubmissionDetailView(APIView):
    """Детали submission для менторов."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, submission_id: str) -> Response:
        """Получить детали submission."""
        user = request.user

        if not can_view_all_submissions(user):
            return Response(
                {"detail": "You don't have permission to view this submission."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        try:
            assignment = Assignment.objects.get(id=submission.assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        lesson_info = None
        module_info = None
        course_info = None

        if assignment.lesson_id:
            try:
                lesson = Lesson.objects.get(id=assignment.lesson_id)
                lesson_info = {
                    "id": str(lesson.id),
                    "title": lesson.title,
                }

                module_info = {
                    "id": str(lesson.module_id),
                    "title": lesson.module.title,
                }

                course_info = {
                    "id": str(lesson.module.course_id),
                    "title": lesson.module.course.title,
                    "slug": lesson.module.course.slug,
                }
            except (Lesson.DoesNotExist, Exception) as e:
                logger.warning(f"Error loading lesson info: {e}")

        
        student_info = None
        try:
            student = User.objects.select_related('info').get(id=submission.student_id)
            student_info = {
                "id": str(student.id),
                "email": student.email,
                "first_name": student.info.first_name if student.info else '',
                "last_name": student.info.last_name if student.info else '',
            }
        except User.DoesNotExist:
            student_info = {
                "id": str(submission.student_id),
                "email": "Unknown",
                "first_name": "Unknown",
                "last_name": "",
            }

        
        revisions = SubmissionRevision.objects.filter(submission=submission).order_by('revision_number')
        revisions_data = []
        for revision in revisions:
            revisions_data.append({
                "id": str(revision.id),
                "revision_number": revision.revision_number,
                "submission_type": revision.submission_type,
                "payload": revision.payload,
                "notes": revision.notes,
                "submitted_at": revision.submitted_at.isoformat() if revision.submitted_at else None,
            })

        
        reviews = SubmissionReview.objects.filter(submission=submission).order_by('-reviewed_at')
        reviews_data = []
        for review in reviews:
            
            reviewer_info = None
            try:
                reviewer = User.objects.select_related('info').get(id=review.mentor_id)
                reviewer_info = {
                    "id": str(reviewer.id),
                    "email": reviewer.email,
                    "first_name": reviewer.info.first_name if reviewer.info else '',
                    "last_name": reviewer.info.last_name if reviewer.info else '',
                }
            except User.DoesNotExist:
                reviewer_info = {
                    "id": str(review.mentor_id),
                    "email": "Unknown",
                    "first_name": "Unknown",
                    "last_name": "",
                }

            reviews_data.append({
                "id": str(review.id),
                "status": review.status,
                "score": str(review.score),
                "max_score": str(review.max_score),
                "feedback": review.feedback,
                "reviewer": reviewer_info,
                "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
            })

        data = {
            "id": str(submission.id),
            "status": submission.status,
            "final_score": str(submission.final_score) if submission.final_score else None,
            "created_at": submission.created_at.isoformat() if submission.created_at else None,
            "first_submitted_at": submission.first_submitted_at.isoformat() if submission.first_submitted_at else None,
            "last_submitted_at": submission.last_submitted_at.isoformat() if submission.last_submitted_at else None,
            "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
            "deadline": submission.deadline.isoformat() if submission.deadline else None,

            
            "assignment": {
                "id": str(assignment.id),
                "title": assignment.title,
                "description": assignment.description,
                "type": assignment.type,
                "max_score": str(assignment.max_score),
            },

            
            "lesson": lesson_info,
            "module": module_info,
            "course": course_info,

            
            "student": student_info,

            
            "revisions": revisions_data,

            
            "reviews": reviews_data,
        }

        return Response(data, status=status.HTTP_200_OK)