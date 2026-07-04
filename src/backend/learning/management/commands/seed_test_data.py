"""
Management command to seed test data for development and testing.

Usage:
    python manage.py seed_test_data
    python manage.py seed_test_data --clear  
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

from src.backend.learning.domain.models.course import Course
from src.backend.learning.domain.models.category import CourseCategory
from src.backend.learning.domain.models.module import Module
from src.backend.learning.domain.models.lesson import Lesson
from src.backend.learning.domain.models.content import LessonContent
from src.backend.assessment.domain.models.assessment import ModuleAssessment
from src.backend.assessment.domain.models.item import AssessmentItem
from src.backend.assessment.domain.models.option import AssessmentOption

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing test data...'))
            self._clear_data()

        self.stdout.write(self.style.SUCCESS('Seeding test data...'))

        with transaction.atomic():
            
            users = self._create_users()
            self.stdout.write(f"✓ Created {len(users)} test users")

            
            categories = self._create_categories()
            self.stdout.write(f"✓ Created {len(categories)} categories")

            
            courses = self._create_courses(users['staff'], categories)
            self.stdout.write(f"✓ Created {len(courses)} courses")

            
            for course in courses:
                modules = self._create_modules(course, users['staff'])
                self.stdout.write(f"✓ Created {len(modules)} modules for {course.title}")

                for module in modules:
                    lessons = self._create_lessons(module, course, users['staff'])
                    self.stdout.write(f"  ✓ Created {len(lessons)} lessons for {module.title}")

                    
                    if module.order == len(modules):
                        assessment = self._create_assessment(module, course, users['staff'])
                        self.stdout.write(f"  ✓ Created assessment for {module.title}")

        self.stdout.write(self.style.SUCCESS('\n✅ Test data seeded successfully!'))
        self.stdout.write('\nTest users created:')
        self.stdout.write(f"  Admin:   admin@learnflow.dev / admin123")
        self.stdout.write(f"  Staff:   staff@learnflow.dev / staff123")
        self.stdout.write(f"  Mentor:  mentor@learnflow.dev / mentor123")
        self.stdout.write(f"  Student: student@learnflow.dev / student123")

    def _clear_data(self):
        """Clear existing test data."""
        LessonContent.objects.filter(lesson__course__title__contains='[TEST]').delete()
        Lesson.objects.filter(course__title__contains='[TEST]').delete()
        Module.objects.filter(course__title__contains='[TEST]').delete()
        ModuleAssessment.objects.filter(course__title__contains='[TEST]').delete()
        Course.objects.filter(title__contains='[TEST]').delete()
        CourseCategory.objects.filter(name__contains='[TEST]').delete()

        
        self.stdout.write(self.style.WARNING('Note: Test users were not deleted'))

    def _create_users(self):
        """Create test users."""
        users = {}

        
        users['admin'], _ = User.objects.get_or_create(
            email='admin@learnflow.dev',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        users['admin'].set_password('admin123')
        users['admin'].save()

        
        users['staff'], _ = User.objects.get_or_create(
            email='staff@learnflow.dev',
            defaults={
                'is_staff': True,
                'is_active': True,
            }
        )
        users['staff'].set_password('staff123')
        users['staff'].save()

        
        users['mentor'], _ = User.objects.get_or_create(
            email='mentor@learnflow.dev',
            defaults={
                'is_active': True,
            }
        )
        users['mentor'].set_password('mentor123')
        users['mentor'].save()

        
        users['student'], _ = User.objects.get_or_create(
            email='student@learnflow.dev',
            defaults={
                'is_active': True,
            }
        )
        users['student'].set_password('student123')
        users['student'].save()

        return users

    def _create_categories(self):
        """Create course categories."""
        categories = []

        categories_data = [
            {'name': '[TEST] Programming', 'slug': 'test-programming'},
            {'name': '[TEST] Web Development', 'slug': 'test-web-development'},
            {'name': '[TEST] Data Science', 'slug': 'test-data-science'},
        ]

        for data in categories_data:
            category, _ = CourseCategory.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'description': f'Test category for {data["name"]}'
                }
            )
            categories.append(category)

        return categories

    def _create_courses(self, creator, categories):
        """Create test courses."""
        courses = []

        courses_data = [
            {
                'title': '[TEST] Python Basics',
                'slug': 'test-python-basics',
                'short_description': 'Learn Python programming from scratch',
                'description': 'A comprehensive course covering Python fundamentals, data structures, and OOP.',
                'category': categories[0],
            },
            {
                'title': '[TEST] Web Development with Django',
                'slug': 'test-django-web-dev',
                'short_description': 'Build modern web applications with Django',
                'description': 'Master Django framework and build production-ready web applications.',
                'category': categories[1],
            },
            {
                'title': '[TEST] Data Analysis with Python',
                'slug': 'test-python-data-analysis',
                'short_description': 'Analyze data using pandas and numpy',
                'description': 'Learn data analysis techniques using Python libraries.',
                'category': categories[2],
            },
        ]

        for data in courses_data:
            course, _ = Course.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    **data,
                    'created_by': creator,
                    'status': 'published',
                }
            )
            courses.append(course)

        return courses

    def _create_modules(self, course, creator):
        """Create modules for a course."""
        modules = []

        if 'Python Basics' in course.title:
            module_titles = [
                'Introduction to Python',
                'Data Types and Variables',
                'Control Flow',
                'Functions and Modules',
            ]
        elif 'Django' in course.title:
            module_titles = [
                'Django Setup',
                'Models and Databases',
                'Views and Templates',
                'Forms and Validation',
            ]
        else:
            module_titles = [
                'Getting Started',
                'Core Concepts',
                'Advanced Topics',
            ]

        for idx, title in enumerate(module_titles, 1):
            module, _ = Module.objects.get_or_create(
                course=course,
                order=idx,
                defaults={
                    'title': title,
                    'description': f'Module covering {title.lower()}',
                }
            )
            modules.append(module)

        return modules

    def _create_lessons(self, module, course, creator):
        """Create lessons for a module."""
        lessons = []

        lesson_count = 3  

        for idx in range(1, lesson_count + 1):
            lesson, created = Lesson.objects.get_or_create(
                module=module,
                order=idx,
                defaults={
                    'title': f'Lesson {idx}: {module.title} Part {idx}',
                    'description': f'Learn about {module.title.lower()} - Part {idx}',
                    'estimated_minutes': 30,
                }
            )

            if created:
                
                LessonContent.objects.create(
                    lesson=lesson,
                    type='text',
                    title=f'Content for {lesson.title}',
                    order=1,
                    body=f"
                    is_required=True,
                )

            lessons.append(lesson)

        return lessons

    def _create_assessment(self, module, course, creator):
        """Create an assessment for a module."""
        assessment, created = ModuleAssessment.objects.get_or_create(
            module_id=module.id,
            defaults={
                'title': f'{module.title} Quiz',
                'created_by_id': creator.id,
                'passing_percentage': Decimal('70.00'),
                'max_attempts': 3,
                'time_limit_minutes': 30,
            }
        )

        if created:
            
            for idx in range(1, 6):
                item = AssessmentItem.objects.create(
                    assessment=assessment,
                    type='multiple_choice',
                    order=idx,
                    title=f'Question {idx}: What is the correct answer for {module.title}?',
                    max_points=Decimal('20.00'),
                )

                
                for opt_idx, letter in enumerate(['A', 'B', 'C', 'D'], 1):
                    AssessmentOption.objects.create(
                        item=item,
                        text=f'Option {letter}',
                        order=opt_idx,
                        is_correct=(opt_idx == 1),  
                    )

        return assessment
