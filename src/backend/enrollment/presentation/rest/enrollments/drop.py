"""
Drop enrollment endpoint — POST /api/v1/enrollment/enrollments/{id}/drop/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.enrollment.application.commands import (
    DropEnrollmentCommand,
    DropEnrollmentHandler,
)
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.presentation.rest.enrollments.serializers import (
    DropEnrollmentSerializer,
    EnrollmentDetailSerializer,
)


class DropEnrollmentView(APIView):
    """
    Drop enrollment — Student drops enrollment.

    POST /api/v1/enrollment/enrollments/{id}/drop/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DropEnrollmentSerializer,
        responses={200: EnrollmentDetailSerializer},
        tags=['Enrollment'],
        operation_id='enrollment_drop',
        summary='Drop enrollment',
        description='Drop enrollment (terminal action)',
    )
    def post(self, request: Request, enrollment_id: str) -> Response:
        """Drop enrollment."""
        
        serializer = DropEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            
            enrollment = CourseEnrollment.objects.get(
                id=UUID(enrollment_id),
                user=request.user
            )

            
            command = DropEnrollmentCommand(
                enrollment_id=enrollment.id,
                reason=serializer.validated_data['reason']
            )

            
            enrollment = DropEnrollmentHandler.handle(command)

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

        
        response_serializer = EnrollmentDetailSerializer(enrollment)
        return Response(response_serializer.data)
