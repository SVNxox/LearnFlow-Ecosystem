"""
Management command для создания тестовых платежей.

Использование:
    python manage.py create_test_payments
    python manage.py create_test_payments --count 50
    python manage.py create_test_payments --clean  
"""

import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from src.backend.payment.domain.models import Payment
from src.backend.learning.domain.models import Course
from src.backend.enrollment.domain.models import CourseEnrollment

User = get_user_model()


def get_field_choices(model, field_name, fallback=None):
    """Получает choices из поля модели или возвращает fallback."""
    field = model._meta.get_field(field_name)
    if field.choices:
        return [choice[0] for choice in field.choices]
    return fallback or []


class Command(BaseCommand):
    help = 'Создаёт тестовые платежи для разработки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Количество платежей для создания (по умолчанию: 20)',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Удалить все существующие платежи перед созданием',
        )

    def handle(self, *args, **options):
        count = options['count']
        clean = options['clean']

        if clean:
            self.stdout.write('Удаляю все платежи...')
            Payment.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Все платежи удалены'))

        
        users = list(User.objects.all()[:10])
        if not users:
            self.stdout.write(self.style.ERROR('✗ Нет пользователей.'))
            return

        
        courses = list(Course.objects.all()[:10])
        if not courses:
            self.stdout.write(self.style.ERROR('✗ Нет курсов.'))
            return

        self.stdout.write(f'Найдено пользователей: {len(users)}')
        self.stdout.write(f'Найдено курсов: {len(courses)}')

        
        valid_statuses = get_field_choices(Payment, 'status', ['pending', 'succeeded', 'failed'])
        valid_methods = get_field_choices(Payment, 'payment_method', ['card', 'cash'])
        valid_providers = get_field_choices(Payment, 'provider', ['stripe', 'payme'])

        
        currency_field = Payment._meta.get_field('currency')
        valid_currencies = [c[0] for c in currency_field.choices] if currency_field.choices else ['UZS', 'USD']

        self.stdout.write(f'Статусы: {valid_statuses}')
        self.stdout.write(f'Методы: {valid_methods}')
        self.stdout.write(f'Провайдеры: {valid_providers}')
        self.stdout.write(f'Валюты: {valid_currencies}')

        created_count = 0

        for i in range(count):
            user = random.choice(users)
            course = random.choice(courses)

            
            enrollment, _ = CourseEnrollment.objects.get_or_create(
                user_id=user.id,
                course_id=course.id,
                defaults={
                    'status': 'active',
                    'delivery_format': random.choice(['online', 'offline']),
                    'enrolled_at': timezone.now() - timedelta(days=random.randint(1, 90)),
                }
            )

            
            status = random.choice(valid_statuses)
            payment_method = random.choice(valid_methods)
            provider = random.choice(valid_providers)
            currency = random.choice(valid_currencies)

            
            if currency == 'UZS':
                amount = Decimal(str(random.randint(50000, 500000)))
            else:
                amount = Decimal(str(random.randint(10, 200)))

            
            created_at = timezone.now() - timedelta(
                days=random.randint(1, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            succeeded_at = None
            failed_at = None
            refunded_at = None

            if status == 'succeeded':
                succeeded_at = created_at + timedelta(minutes=random.randint(1, 30))
            elif status == 'failed':
                failed_at = created_at + timedelta(minutes=random.randint(1, 10))
            elif status == 'refunded':
                succeeded_at = created_at + timedelta(minutes=random.randint(1, 30))
                refunded_at = succeeded_at + timedelta(days=random.randint(1, 30))

            
            Payment.objects.create(
                user_id=user.id,
                enrollment_id=enrollment.id,
                amount=amount,
                currency=currency,
                status=status,
                payment_method=payment_method,
                provider=provider,  
                provider_payment_id=f"test_{random.randint(100000, 999999)}",
                idempotency_key=f"idem_{random.randint(100000, 999999)}",
                created_at=created_at,
                succeeded_at=succeeded_at,
                failed_at=failed_at,
                refunded_at=refunded_at,
                metadata={
                    'test': True,
                    'created_by': 'management_command',
                }
            )

            created_count += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'Создано {i + 1} платежей...')

        self.stdout.write(self.style.SUCCESS(f'\n✓ Создано {created_count} тестовых платежей'))

        
        for s in valid_statuses:
            c = Payment.objects.filter(status=s).count()
            if c > 0:
                self.stdout.write(f'  - {s}: {c}')