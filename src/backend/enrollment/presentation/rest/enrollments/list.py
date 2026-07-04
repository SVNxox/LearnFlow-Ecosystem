"""
List enrollments endpoint — GET /api/v1/enrollment/enrollments/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from src.backend.enrollment.application.queries import (
    MyEnrollmentsQuery,
    MyEnrollmentsHandler,
    AdminEnrollmentsQuery,
    AdminEnrollmentsHandler,
)
from src.backend.enrollment.presentation.rest.enrollments.serializers import (
    EnrollmentListSerializer,
)


class ListEnrollmentsView(APIView):
    """
    List enrollments.

    - Regular users: see their own enrollments
    - Admin users: see all enrollments with filters

    GET /api/v1/enrollment/enrollments/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: EnrollmentListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                required=False,
                description='Filter by status (pending/active/suspended/dropped/completed)'
            ),
            OpenApiParameter(
                name='course_id',
                type=str,
                required=False,
                description='Filter by course ID (admin only)'
            ),
            OpenApiParameter(
                name='student_id',
                type=str,
                required=False,
                description='Filter by student ID (admin only)'
            ),
            OpenApiParameter(
                name='page',
                type=int,
                required=False,
                description='Page number (admin only, default: 1)'
            ),
        ],
        tags=['Enrollment'],
        operation_id='enrollment_list',
        summary='List enrollments',
        description='List enrollments (own for students, all for admins)',
    )
    def get(self, request: Request) -> Response:
        """List enrollments."""

        
        is_admin = request.user.has_role('admin')

        if is_admin:
            
            query = AdminEnrollmentsQuery(
                course_id=request.query_params.get('course_id'),
                student_id=request.query_params.get('student_id'),
                status=request.query_params.get('status'),
                page=int(request.query_params.get('page', 1)),
                page_size=20,
            )
            result = AdminEnrollmentsHandler.handle(query)

            
            serializer = EnrollmentListSerializer(result['results'], many=True)

            return Response({
                'results': serializer.data,
                'count': result['count'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages'],
            })
        else:
            
            query = MyEnrollmentsQuery(
                user_id=request.user.id,
                status=request.query_params.get('status')
            )
            enrollments = MyEnrollmentsHandler.handle(query)
            serializer = EnrollmentListSerializer(enrollments, many=True)
            return Response(serializer.data)
