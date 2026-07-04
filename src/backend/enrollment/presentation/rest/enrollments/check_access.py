"""
Check access endpoint — GET /api/v1/enrollment/enrollments/{id}/check-access/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.enrollment.application.queries import (
    CheckAccessQuery,
    CheckAccessHandler,
)
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.presentation.rest.enrollments.serializers import (
    CheckAccessRequestSerializer,
    CheckAccessResponseSerializer,
)


class CheckAccessView(APIView):
    """
    Check access — Check if student can access content.

    GET /api/v1/enrollment/enrollments/{id}/check-access/?content_id={uuid}
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[CheckAccessRequestSerializer],
        responses={200: CheckAccessResponseSerializer},
        tags=['Enrollment'],
        operation_id='enrollment_check_access',
        summary='Check content access',
        description='Check if student can access specific content',
    )
    def get(self, request: Request, enrollment_id: str) -> Response:
        """Check access."""
        
        request_serializer = CheckAccessRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        try:
            
            enrollment = CourseEnrollment.objects.get(
                id=UUID(enrollment_id),
                user=request.user
            )

            
            query = CheckAccessQuery(
                user_id=request.user.id,
                course_id=enrollment.course_id,
                content_id=request_serializer.validated_data['content_id']
            )

            
            can_access, reason = CheckAccessHandler.handle(query)

        except CourseEnrollment.DoesNotExist:
            return Response(
                {'error': 'Enrollment not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        response_data = {
            'can_access': can_access,
            'reason': reason
        }
        response_serializer = CheckAccessResponseSerializer(response_data)
        return Response(response_serializer.data)
