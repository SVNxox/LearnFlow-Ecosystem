"""
Enrollment detail endpoint — GET /api/v1/enrollment/enrollments/{id}/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.enrollment.application.queries import (
    EnrollmentDetailQuery,
    EnrollmentDetailHandler,
)
from src.backend.enrollment.presentation.rest.enrollments.serializers import (
    EnrollmentDetailSerializer,
)


class EnrollmentDetailView(APIView):
    """
    Enrollment detail — Get enrollment by ID.

    GET /api/v1/enrollment/enrollments/{id}/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: EnrollmentDetailSerializer},
        tags=['Enrollment'],
        operation_id='enrollment_detail',
        summary='Get enrollment details',
        description='Get enrollment details by ID',
    )
    def get(self, request: Request, enrollment_id: str) -> Response:
        """Get enrollment detail."""
        try:
            
            query = EnrollmentDetailQuery(
                enrollment_id=UUID(enrollment_id),
                user_id=request.user.id
            )

            
            enrollment = EnrollmentDetailHandler.handle(query)

        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        
        serializer = EnrollmentDetailSerializer(enrollment)
        return Response(serializer.data)
