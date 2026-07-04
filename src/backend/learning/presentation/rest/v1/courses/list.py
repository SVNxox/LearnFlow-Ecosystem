from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.application.queries import CourseCatalogQuery
from src.backend.learning.application.queries.course_admin import CourseAdminQuery


class CourseListView(APIView):
    """
    GET /api/learning/ — список курсов.

    Для admin/staff: все курсы (draft, published, archived)
    Для mentor/student/анонимов: только published курсы
    """

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        
        category_slug = request.query_params.get("category")
        delivery_format = request.query_params.get("format")
        language = request.query_params.get("language")
        search_query = request.query_params.get("search")
        status_filter = request.query_params.get("status")

        
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)

        
        user_roles = []
        if request.user and request.user.is_authenticated:
            user_roles = request.user.get_roles()  

        is_admin_or_staff = 'admin' in user_roles or 'staff' in user_roles

        
        if is_admin_or_staff:
            
            if search_query:
                courses = CourseAdminQuery.search_courses(
                    query=search_query,
                    status_filter=status_filter,
                    language=language,
                )
            else:
                courses = CourseAdminQuery.get_all_courses(
                    status_filter=status_filter,
                    category_slug=category_slug,
                    delivery_format=delivery_format,
                    language=language,
                )
        else:
            
            if search_query:
                courses = CourseCatalogQuery.search_courses(
                    query=search_query,
                    language=language,
                )
            else:
                courses = CourseCatalogQuery.get_published_courses(
                    category_slug=category_slug,
                    delivery_format=delivery_format,
                    language=language,
                )

        
        start = (page - 1) * page_size
        end = start + page_size
        total_count = courses.count()
        paginated_courses = courses[start:end]

        
        from src.backend.enrollment.models import CourseEnrollment
        from django.db.models import Count as DjangoCount

        course_ids = [course.id for course in paginated_courses]
        enrollment_counts = {}
        if course_ids:
            counts = CourseEnrollment.objects.filter(
                course_id__in=course_ids,
                status='active',
                deleted_at__isnull=True
            ).values('course_id').annotate(count=DjangoCount('id'))
            enrollment_counts = {str(item['course_id']): item['count'] for item in counts}

        
        results = [
            {
                "id": str(course.id),
                "title": course.title,
                "slug": course.slug,
                "short_description": course.short_description,
                "thumbnail_url": course.thumbnail_url,
                "category": {
                    "name": course.category.name,
                    "slug": course.category.slug,
                } if course.category else None,
                "estimated_weeks": course.estimated_weeks,
                "active_enrollment_count": enrollment_counts.get(str(course.id), 0),
                "supports_online": course.supports_online,
                "supports_offline": course.supports_offline,
                "language": course.language,
                "status": course.status,
                
                "price": str(course.price) if course.price is not None else "0",
                "currency": course.currency or "UZS",
            }
            for course in paginated_courses
        ]

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )