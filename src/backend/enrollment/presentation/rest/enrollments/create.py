"""
Create enrollment endpoint — POST /api/v1/enrollment/enrollments/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.enrollment.application.commands import (
    EnrollStudentCommand,
    EnrollStudentHandler,
)
from src.backend.enrollment.presentation.rest.enrollments.serializers import (
    EnrollmentCreateSerializer,
    EnrollmentDetailSerializer,
)


class CreateEnrollmentView(APIView):
    """
    Create enrollment — Student enrolls in course.

    POST /api/v1/enrollment/enrollments/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EnrollmentCreateSerializer,
        responses={201: EnrollmentDetailSerializer},
        tags=['Enrollment'],
        operation_id='enrollment_create',
        summary='Enroll in course',
        description='Enroll authenticated user in a course',
    )
    def post(self, request: Request) -> Response:
        """Create enrollment."""
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        command = EnrollStudentCommand(
            user_id=request.user.id,
            course_id=serializer.validated_data['course_id'],
            delivery_format=serializer.validated_data['delivery_format'],
            access_level=serializer.validated_data.get('access_level', 'full'),
            enrolled_by_id=request.user.id,
        )

        
        try:
            enrollment = EnrollStudentHandler.handle(command)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        response_serializer = EnrollmentDetailSerializer(enrollment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
