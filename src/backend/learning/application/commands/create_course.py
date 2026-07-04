"""
CreateCourseCommand — создание нового курса.

Business Rules:
- Курс создаётся в статусе 'draft'
- Slug автоматически генерируется из title (можно переопределить)
- Slug уникален (проверка перед созданием)
- created_by = текущий пользователь
- По умолчанию supports_online=True, supports_offline=False

Permissions:
- Admin или Staff могут создавать курсы
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from src.backend.core.exceptions import AccessDeniedError, BusinessValidationError, NotFoundError
from src.backend.learning.domain.models import Course, CourseCategory

User = get_user_model()


@dataclass
class CreateCourseData:
    """Input data для создания курса."""

    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category_id: Optional[str] = None
    status: str = "draft"
    supports_online: bool = True
    supports_offline: bool = False
    language: str = "ru"
    estimated_weeks: Optional[int] = None
    is_sequential: bool = True
    slug: Optional[str] = None  
    price: str = "0"  
    currency: str = "UZS"


class CreateCourseCommand:
    """
    Command для создания курса.

    Permissions:
    - Admin или Staff (course authoring)
    """

    @staticmethod
    @transaction.atomic
    def execute(data: CreateCourseData, actor: User) -> Course:
        """
        Создаёт новый курс в статусе draft.

        Args:
            data: CreateCourseData с параметрами курса
            actor: Пользователь создающий курс (должен быть admin или staff)

        Returns:
            Course instance (status='draft')

        Raises:
            AccessDeniedError: если actor не admin/staff
            BusinessValidationError: если данные невалидны или slug занят
            NotFoundError: если категория не найдена
        """
        
        user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []
        is_admin = 'admin' in user_roles
        is_staff = 'staff' in user_roles

        if not (is_admin or is_staff):
            raise AccessDeniedError(
                "Only admin or staff can create courses",
                code="insufficient_permissions"
            )

        
        clean_title = data.title.strip()
        if len(clean_title) < 3:
            raise BusinessValidationError(
                code="title_too_short",
                lang="uz",
                message="Course title must be at least 3 characters long"
            )

        
        slug = data.slug.strip() if data.slug else slugify(clean_title)
        if not slug:
            raise BusinessValidationError(
                code="slug_required",
                lang="uz",
                message="Slug is required or must be generated from title"
            )

        
        if Course.objects.filter(slug=slug).exists():
            raise BusinessValidationError(
                code="slug_already_exists",
                lang="uz",
                message=f"Course with slug '{slug}' already exists"
            )

        
        if not data.supports_online and not data.supports_offline:
            raise BusinessValidationError(
                code="invalid_delivery_format",
                lang="uz",
                message="Course must support at least one delivery format (online or offline)"
            )

        
        if data.estimated_weeks is not None and data.estimated_weeks <= 0:
            raise BusinessValidationError(
                code="invalid_estimated_weeks",
                lang="uz",
                message="Estimated weeks must be greater than 0"
            )

        
        if data.category_id:
            if not CourseCategory.objects.filter(
                id=data.category_id, is_active=True
            ).exists():
                raise NotFoundError(
                    f"Category {data.category_id} not found or inactive",
                    code="category_not_found"
                )

        
        course = Course.objects.create(
            title=clean_title,
            slug=slug,
            description=data.description,
            short_description=data.short_description,
            thumbnail_url=data.thumbnail_url,
            category_id=data.category_id,
            status=data.status,  
            supports_online=data.supports_online,
            supports_offline=data.supports_offline,
            language=data.language,
            estimated_weeks=data.estimated_weeks,
            is_sequential=data.is_sequential,
            price=Decimal(data.price) if data.price else Decimal('0'),  
            currency=data.currency or 'UZS',
            created_by=actor,
        )

        
        

        return course