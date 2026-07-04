



LearnFlow использует **пирамиду тестирования**:
- 70% — Unit tests (selectors, services, бизнес-логика)
- 20% — Integration tests (cross-domain flows, events)
- 10% — E2E tests (критические user journeys)

**Правило:** Тесты должны быть **быстрыми**, **изолированными** и **детерминированными**.

---



```
apps/courses/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           
│   ├── test_models.py        
│   ├── test_selectors.py     
│   ├── test_services.py      
│   ├── test_events.py        
│   └── test_api.py           
```

---



**Что тестировать:**
- Корректность фильтрации и сортировки
- Visibility rules (кто что видит)
- Annotations и aggregations
- Edge cases (пустые результаты, несуществующие ID)

**Пример:**

```python

import pytest
from apps.courses.selectors import CourseCatalogSelector

class TestCourseCatalogSelector:
    def test_get_published_courses_filters_by_status(self, db, published_course, draft_course):
        """Selector возвращает только published курсы."""
        result = CourseCatalogSelector.get_published_courses(filters={})
        assert published_course in result
        assert draft_course not in result

    def test_get_published_courses_filters_by_category(self, db, backend_course, frontend_course):
        """Фильтрация по category slug работает."""
        result = CourseCatalogSelector.get_published_courses(filters={'category_slug': 'backend'})
        assert backend_course in result
        assert frontend_course not in result

    def test_get_published_courses_excludes_deleted(self, db, published_course):
        """Soft-deleted курсы не возвращаются."""
        published_course.deleted_at = timezone.now()
        published_course.save()
        result = CourseCatalogSelector.get_published_courses(filters={})
        assert published_course not in result
```

---



**Что тестировать:**
- Успешный путь (happy path)
- Бизнес-правила (BR-*) — негативные тесты
- Валидация входных данных
- Транзакционность (rollback при ошибке)
- Event dispatch (что события диспетчеризируются)

**Пример:**

```python

import pytest
from django.core.exceptions import ValidationError
from apps.courses.services import CourseService
from apps.courses.events import CoursePublished

class TestCourseService:
    def test_publish_course_success(self, db, staff_user, draft_course_with_module):
        """Нормальный путь: курс с модулями публикуется."""
        course = CourseService.publish_course(draft_course_with_module.id, staff_user)
        assert course.status == 'published'

    def test_publish_course_no_modules_raises(self, db, staff_user, empty_draft_course):
        """BR-06: нельзя опубликовать пустой курс."""
        with pytest.raises(ValidationError, match="published module"):
            CourseService.publish_course(empty_draft_course.id, staff_user)

    def test_publish_emits_event(self, db, staff_user, publishable_course, mocker):
        """Событие диспетчеризируется после commit."""
        mock = mocker.patch('apps.learning.events.dispatch')
        CourseService.publish_course(publishable_course.id, staff_user)
        mock.assert_called_once()
        assert isinstance(mock.call_args[0][0], CoursePublished)

    def test_publish_rollback_on_error(self, db, staff_user, draft_course, mocker):
        """При ошибке транзакция откатывается."""
        mocker.patch('apps.learning.services.some_external_call', side_effect=Exception)
        with pytest.raises(Exception):
            CourseService.publish_course(draft_course.id, staff_user)
        draft_course.refresh_from_db()
        assert draft_course.status == 'draft'  
```

---



**Что тестировать:**
- Cross-domain event flow (emit → handler → side effect)
- Идемпотентность handlers (вызов дважды = тот же результат)
- Транзакционность (handler не должен видеть uncommitted данные)

**Пример:**

```python

import pytest
from apps.courses.events import student_enrolled, StudentEnrolled
from apps.progress.models import CourseProgress

class TestStudentEnrolledHandler:
    def test_creates_progress_record(self, db, enrollment):
        """Handler создаёт CourseProgress при StudentEnrolled."""
        assert not CourseProgress.objects.filter(enrollment_id=enrollment.id).exists()
        
        event = StudentEnrolled(
            enrollment_id=enrollment.id,
            user_id=enrollment.user.id,
            course_id=enrollment.course.id,
            delivery_format='online',
        )
        student_enrolled.send(sender=StudentEnrolled, event=event)
        
        progress = CourseProgress.objects.get(enrollment_id=enrollment.id)
        assert progress.status == 'not_started'
        assert progress.total_modules_count == enrollment.course.modules.count()

    def test_idempotent(self, db, enrollment):
        """Повторный вызов handler не создаёт дубликатов."""
        event = StudentEnrolled(...)
        student_enrolled.send(sender=StudentEnrolled, event=event)
        student_enrolled.send(sender=StudentEnrolled, event=event)  
        
        assert CourseProgress.objects.filter(enrollment_id=enrollment.id).count() == 1
```

---



**Что тестировать:**
- Lesson completed → Module completion check
- Module completed → Course completion check
- Атомарность инкрементов (F() expressions)
- Блокировки (select_for_update)

**Пример:**

```python

import pytest
from apps.progress.services import LessonProgressService

class TestCascadeCompletion:
    def test_last_lesson_completes_module(self, db, enrollment, module_with_3_lessons):
        """Завершение последнего урока завершает модуль."""
        lessons = module_with_3_lessons.lessons.all()
        
        
        LessonProgressService.mark_lesson_completed(enrollment.id, lessons[0].id)
        LessonProgressService.mark_lesson_completed(enrollment.id, lessons[1].id)
        
        mp = ModuleProgress.objects.get(enrollment_id=enrollment.id, module_id=module_with_3_lessons.id)
        assert mp.status == 'in_progress'
        assert mp.completed_lessons_count == 2
        
        
        LessonProgressService.mark_lesson_completed(enrollment.id, lessons[2].id)
        
        mp.refresh_from_db()
        assert mp.status == 'completed'
        assert mp.completed_lessons_count == 3
        assert mp.completed_at is not None

    def test_race_condition_protected(self, db, enrollment, lesson, mocker):
        """select_for_update защищает от race conditions."""
        
        
        pass
```

---



**Что тестировать:**
- HTTP status codes (200, 201, 400, 403, 404)
- Response format (JSON structure)
- Permissions (каждая роль для каждого endpoint)
- Query parameters (pagination, filtering, ordering)

**Пример:**

```python

import pytest
from rest_framework.test import APIClient

class TestCourseListAPI:
    def test_anonymous_can_view_published(self, db, api_client, published_course):
        """Анонимный пользователь видит published курсы."""
        response = api_client.get('/api/v1/learning/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(published_course.id)

    def test_anonymous_cannot_view_drafts(self, db, api_client, draft_course):
        """Анонимный пользователь не видит draft курсы."""
        response = api_client.get('/api/v1/learning/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_staff_can_view_own_drafts(self, db, authenticated_client_staff, draft_course):
        """Staff видит свои черновики."""
        response = authenticated_client_staff.get('/api/v1/learning/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_staff_cannot_view_other_drafts(self, db, authenticated_client_staff, draft_course_other):
        """Staff не видит чужие черновики."""
        response = authenticated_client_staff.get('/api/v1/learning/')
        assert len(response.data['results']) == 0
```

---



**Что тестировать:**
- Критические user flows end-to-end
- Интеграция всех слоёв (API → Service → Event → другой Domain)

**Пример:**

```python

import pytest

class TestEnrollmentFlow:
    def test_student_enrolls_and_progresses(
        self, db, api_client, student_user, published_course_with_lessons
    ):
        """E2E: студент записывается и проходит первый урок."""
        client = api_client
        client.force_authenticate(user=student_user)
        
        
        response = client.post('/api/v1/enrollments/', {
            'course_id': str(published_course_with_lessons.id)
        })
        assert response.status_code == 201
        enrollment_id = response.data['id']
        
        
        response = client.get(f'/api/v1/progress/learning/{enrollment_id}/')
        assert response.status_code == 200
        assert response.data['status'] == 'not_started'
        
        
        lesson_id = published_course_with_lessons.modules.first().lessons.first().id
        response = client.post(f'/api/v1/progress/lessons/{lesson_id}/start/')
        assert response.status_code == 200
        
        
        response = client.post(f'/api/v1/progress/lessons/{lesson_id}/complete/')
        assert response.status_code == 200
        
        
        response = client.get(f'/api/v1/progress/learning/{enrollment_id}/')
        assert response.data['completed_lessons_count'] == 1
```

---



**Используй `conftest.py` для переиспользуемых fixtures:**

```python

import pytest
from apps.accounts.models import User
from apps.courses.models import Course, Module, Lesson

@pytest.fixture
def staff_user(db):
    """Создаёт пользователя с ролью Staff."""
    user = User.objects.create_user(email='staff@test.com', password='password')
    user.roles.create(name='staff')
    return user

@pytest.fixture
def published_course(db, staff_user):
    """Создаёт published курс."""
    return Course.objects.create(
        title='Test Course',
        slug='test-course',
        status='published',
        created_by=staff_user,
    )

@pytest.fixture
def draft_course_with_module(db, staff_user):
    """Создаёт draft курс с одним модулем."""
    course = Course.objects.create(
        title='Draft Course',
        slug='draft-course',
        status='draft',
        created_by=staff_user,
    )
    Module.objects.create(
        course=course,
        title='Module 1',
        order_index=1,
        is_published=True,
    )
    return course
```

---



**Минимальные требования:**
- **Selectors:** 90%+ coverage
- **Services:** 95%+ coverage (все бизнес-правила)
- **API:** 80%+ coverage (основные paths + permissions)
- **Events:** 100% coverage (критично для cross-domain)

**Запуск:**

```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

---





```python
def test_handler_idempotent(db, enrollment):
    """Handler можно вызвать дважды без side effects."""
    event = StudentEnrolled(...)
    
    
    handler(event)
    state_1 = CourseProgress.objects.get(enrollment_id=enrollment.id)
    
    
    handler(event)
    state_2 = CourseProgress.objects.get(enrollment_id=enrollment.id)
    
    assert state_1 == state_2  
```



```python
def test_counter_atomic(db, module_progress):
    """F() expressions обеспечивают атомарный инкремент."""
    initial = module_progress.completed_lessons_count
    
    
    ModuleProgress.objects.filter(pk=module_progress.pk).update(
        completed_lessons_count=F('completed_lessons_count') + 1
    )
    ModuleProgress.objects.filter(pk=module_progress.pk).update(
        completed_lessons_count=F('completed_lessons_count') + 1
    )
    
    module_progress.refresh_from_db()
    assert module_progress.completed_lessons_count == initial + 2
```



```python
def test_submission_versioning(db, submission, student_user):
    """Каждая попытка создаёт новый SubmissionRevision."""
    rev1 = SubmissionService.submit_revision(submission.id, 'v1', student_user)
    rev2 = SubmissionService.submit_revision(submission.id, 'v2', student_user)
    
    assert rev1.version_number == 1
    assert rev2.version_number == 2
    assert submission.revisions.count() == 2
    assert submission.current_revision == rev2
```

---



**GitHub Actions / GitLab CI:**

```yaml
test:
  script:
    - pip install -r requirements.txt
    - pytest --cov=apps --cov-fail-under=85
    - pytest --ds=config.settings.test --reuse-db
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

**Pre-commit hook:**

```bash


pytest apps/ -x  
```

---



- ❌ Django framework internals (не тестируй что `save()` работает)
- ❌ Third-party libraries (не тестируй DRF serializers)
- ❌ Тривиальные геттеры/сеттеры
- ❌ `__str__` методы (если только не критично для бизнеса)

---



| Инструмент | Назначение |
|------------|------------|
| `pytest-django` | Django integration для pytest |
| `pytest-cov` | Coverage reports |
| `pytest-xdist` | Parallel test execution |
| `factory_boy` | Альтернатива fixtures (более гибкие) |
| `freezegun` | Мокирование времени |
| `responses` | Мокирование HTTP requests |

---



1. Настроить pytest в `pytest.ini`
2. Создать базовые fixtures в `conftest.py`
3. Начать с unit tests для Services (highest ROI)
4. Добавить integration tests для событий
5. Добавить API tests для критичных endpoints
6. Настроить CI/CD pipeline
