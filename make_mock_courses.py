cd /home/svn/PyCharmMiscProject/DjangoProject/LearnFlow\ Ecosystem/learnflow && DJANGO_SETTINGS_MODULE=learnflow.settings.local python manage.py shell
   -c "
   from src.backend.learning.domain.models import Course, CourseCategory
   from src.backend.identity.models import User

   
   category, _ = CourseCategory.objects.get_or_create(
       slug='programming',
       defaults={'name': 'Programming', 'description': 'Programming courses'}
   )
   print(f'✅  Category: {category.name}')

   
   staff_user = User.objects.filter(is_staff=True).first()
   if not staff_user:
       staff_user = User.objects.create_user(
           email='staff@learnflow.uz',
           password='staff123',
           is_staff=True,
           is_active=True
       )
       print(f'✅  Created staff: {staff_user.email}')
   else:
       print(f'✅  Staff exists: {staff_user.email}')

   
   courses_data = [
       {
           'slug': 'python-beginners',
           'title': 'Python для начинающих',
           'short_description': 'Изучите основы Python с нуля',
           'description': 'Полный курс Python для новичков. Изучите синтаксис, структуры данных, ООП и многое другое.',
           'status': 'published',
           'estimated_weeks': 8,
       },
       {
           'slug': 'web-development',
           'title': 'Web Development',
           'short_description': 'Создайте свой первый веб-сайт',
           'description': 'Изучите HTML, CSS, JavaScript и создайте полноценный веб-сайт.',
           'status': 'published',
           'estimated_weeks': 12,
       },
       {
           'slug': 'data-science',
           'title': 'Data Science Basics',
           'short_description': 'Введение в анализ данных',
           'description': 'Изучите основы анализа данных, визуализацию и машинное обучение.',
           'status': 'draft',
           'estimated_weeks': 16,
       }
   ]

   for data in courses_data:
       course, created = Course.objects.get_or_create(
           slug=data['slug'],
           defaults={
               **data,
               'category': category,
               'supports_online': True,
               'supports_offline': True,
               'language': 'ru',
               'created_by': staff_user
           }
       )
       status = '✅  Created' if created else '✅  Exists'
       print(f'{status}: {course.title} ({course.status})')

   print(f'\\n✅  Total courses: {Course.objects.count()}')
   print(f'✅  Published courses: {Course.objects.filter(status=\"published\").count()}')
   "