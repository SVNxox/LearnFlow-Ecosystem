

**Version:** MVP 95%  
**Date:** 2026-06-16  
**Language:** Uzbek (primary), Russian, English

---





```
1. Открыть learnflow.uz
   └─> Главная страница (public)

2. Нажать "Ro'yxatdan o'tish" (Register)
   └─> /register

3. Заполнить форму регистрации
   ├─ Email: student@example.com
   ├─ Parol: SecurePass123
   ├─ Ism: Alisher
   └─ Familiya: Umarov

4. Нажать "Ro'yxatdan o'tish"
   └─> Backend: POST /api/v1/identity/auth/register/
       ├─ Создаёт User (is_active=False)
       ├─ Создаёт UserInfo, UserSettings
       ├─ Назначает роль "Student"
       ├─ Создаёт StudentProfile
       ├─ Генерирует EmailVerificationToken
       └─> Отправляет email (Celery task)

5. Редирект на /verify-email?email=student@example.com
   └─> Показывает инструкции на узбекском:
       ├─ "Emailni tekshiring"
       ├─ "Tasdiqlash havolasi yuborildi"
       ├─ Пошаговые инструкции (1-4)
       └─ Кнопка "Emailni qayta yuboring" (120s cooldown)

6. Открыть email inbox
   └─> Получить письмо от LearnFlow
       └─> Subject: "Verify your email - LearnFlow"

7. Нажать на verification link
   └─> /verify-email?token=abc123xyz...
       └─> Backend: GET /api/v1/identity/auth/verify-email/
           ├─ Проверяет token валиден
           ├─ Устанавливает User.is_active = True
           └─> Возвращает успех

8. Редирект на /login?verified=1
   └─> Показывает: "✅ Email tasdiqlandi!"

9. Войти в систему
   ├─ Email: student@example.com
   └─ Parol: SecurePass123
       └─> Backend: POST /api/v1/identity/auth/login/
           ├─ Проверяет credentials
           ├─ Проверяет is_active = True
           ├─ Генерирует access_token (JWT, 15 min)
           ├─ Генерирует refresh_token (30 days)
           └─> Возвращает токены

10. Редирект на /dashboard/student
    └─> Student Dashboard
        ├─ Мои курсы (enrollments)
        ├─ Прогресс
        ├─ Предстоящие дедлайны
        └─> Рекомендованные курсы

11. Нажать "Курслар" (Courses)
    └─> /courses
        └─> Каталог курсов (public)
            ├─ Фильтры (категория, статус)
            ├─ Поиск
            └─> Список курсов

12. Выбрать курс "Python для начинающих"
    └─> /courses/python-beginners
        └─> Детальная страница курса
            ├─ Описание
            ├─ Программа (модули + уроки)
            ├─ Цена / Бесплатно
            ├─ Формат (online / offline / оба)
            └─> Кнопка "Yozilish" (Enroll)

13. Нажать "Yozilish"
    └─> Модальное окно:
        ├─ Выбрать формат: [online] или [offline]
        └─> Подтвердить

14. Подтвердить запись
    └─> Backend: POST /api/v1/enrollment/enroll/
        ├─ course_id: uuid
        ├─ delivery_format: "online"
        └─> Создаёт CourseEnrollment
            ├─ status: "active"
            ├─ enrolled_at: now()
            └─> Событие: StudentEnrolled (Outbox)

15. Событие StudentEnrolled обрабатывается
    └─> Progress Domain:
        └─> Инициализирует прогресс
            ├─ CourseProgress (0% completion)
            ├─ ModuleProgress для каждого модуля
            └─ LessonProgress для каждого урока

16. Редирект на /courses/python-beginners?enrolled=1
    └─> Показывает: "✅ Siz kursga yozildingiz!"
    └─> Кнопка "Boshlash" появляется

17. Нажать "Boshlash"
    └─> Редирект на первый урок
        └─> /courses/python-beginners/lessons/{lesson_id}

18. Просмотр урока
    └─> Lesson Page
        ├─ Video content (если есть)
        ├─ Text content
        ├─ Code examples
        ├─ Downloadable materials
        └─> Навигация (prev / next)

19. Просмотр контента
    └─> Frontend отправляет прогресс
        └─> Backend: POST /api/v1/progress/content-view/
            ├─ enrollment_id
            ├─ content_id
            ├─ duration_seconds
            └─> Обновляет LessonProgress
                └─> viewed_contents += content_id

20. Завершить урок (все контенты просмотрены)
    └─> Backend автоматически:
        ├─ LessonProgress.status = "completed"
        ├─ LessonProgress.completed_at = now()
        └─> Событие: LessonCompleted (Signal)

21. Событие LessonCompleted → проверка Module
    └─> Progress Domain:
        └─> Проверяет все уроки модуля завершены?
            ├─ Да → ModuleProgress.status = "completed"
            │       └─> Событие: ModuleCompleted (Signal)
            └─ Нет → продолжить обучение

22. Событие ModuleCompleted → открывает Assessment
    └─> Assessment Domain:
        └─> ModuleAssessment становится доступным
            └─> Показывает в UI: "Testni boshlang"

23. Нажать "Testni boshlang"
    └─> /assessments/{assessment_id}
        └─> Assessment Detail Page
            ├─ Описание
            ├─ Количество вопросов
            ├─ Проходной балл
            ├─ Время (если лимит)
            └─> Кнопка "Boshlash"

24. Начать assessment
    └─> Backend: POST /api/v1/assessment/attempts/
        ├─ enrollment_id
        ├─ assessment_id
        └─> Создаёт AssessmentAttempt
            ├─ attempt_number: 1
            ├─ started_at: now()
            ├─ expires_at: now() + time_limit (если есть)
            └─> Возвращает attempt_id

25. Редирект на /assessments/{id}/attempt/{attempt_id}
    └─> Assessment Attempt Page
        ├─ Таймер (если лимит)
        ├─ Progress bar (вопросы)
        └─> Вопросы по частям (parts)

26. Отвечать на вопросы
    └─> Для каждого вопроса:
        └─> Backend: POST /api/v1/assessment/attempts/{id}/responses/
            ├─ item_id
            ├─ selected_option_ids (quiz)
            │   ИЛИ
            ├─ text_response (essay)
            │   ИЛИ
            └─ submitted_code (coding)

27. Завершить assessment
    └─> Backend: POST /api/v1/assessment/attempts/{id}/finalize/
        └─> Assessment Domain:
            ├─ Auto-grade quiz questions
            ├─ Essay/Coding → pending_review
            ├─> Вычисляет total_score
            └─> Устанавливает attempt.status
                ├─ "passed" (если score >= passing_score)
                ├─ "failed" (если score < passing_score)
                └─ "pending_review" (если есть manual items)

28. Если passed → событие AssessmentPassed
    └─> Progress Domain:
        └─> Разблокирует следующий модуль
            └─> ModuleProgress.status = "unlocked"

29. Если pending_review → ждать ментора
    └─> Показывает: "Mentor tekshirmoqda..."

30. Продолжить следующий модуль
    └─> Повторить шаги 17-28 для каждого модуля

31. Завершить все модули + assessments
    └─> Backend автоматически:
        └─> CourseProgress.status = "completed"
            └─> Событие: CourseCompleted (Outbox)

32. Событие CourseCompleted → генерация сертификата
    └─> Certificates Domain:
        └─> Создаёт Certificate
            ├─ verification_code (6 символов)
            ├─ issue_date: now()
            ├─ Snapshot данных (course_title, user_name)
            └─> Генерирует PDF (Celery task)

33. Сертификат готов
    └─> Email notification: "Tabriklaymiz! Sertifikat tayyor!"
    └─> Dashboard показывает: "🎓 Yangi sertifikat"

34. Скачать сертификат
    └─> /certificates/{id}/download
        └─> Скачивает PDF
```

---



```
1-4. Как в Сценарии 1 (регистрация)

5. Редирект на /verify-email
   └─> Но студент ЗАКРЫЛ страницу (не верифицировал)

6. На следующий день: хочет войти
   └─> /login
       ├─ Email: student@example.com
       └─ Parol: SecurePass123
           └─> Backend: 401 Unauthorized
               └─> Error: "Email tasdiqlanmagan. Pochta qutingizni tekshiring."

7. Студент забыл / потерял email
   └─> Решает: "Заново зарегистрируюсь"

8. Идёт на /register
   ├─ Вводит ТОТ ЖЕ email
   └─ Нажимает "Ro'yxatdan o'tish"

9. Backend: POST /api/v1/identity/auth/register/
   └─> Проверяет: email существует?
       ├─ is_active = False → УДАЛЯЕТ старый аккаунт
       └─> Создаёт НОВЫЙ аккаунт
           └─> Отправляет новый verification email

10. Редирект на /verify-email
    └─> Показывает новые инструкции

11. На этот раз: открывает email И верифицирует
    └─> Продолжает как Сценарий 1 с шага 7
```

**Важно:** Старые данные (если были) УДАЛЕНЫ. Это новый аккаунт.

---



```
1. Студент на /login
   └─> Не помнит пароль

2. Нажать "Parolni unutdingizmi?"
   └─> /password-reset

3. Ввести email
   ├─ Email: student@example.com
   └─> Backend: POST /api/v1/identity/auth/password-reset/
       ├─ Проверяет: user существует И is_active = True
       ├─> Генерирует PasswordResetToken (1 hour)
       └─> Отправляет email (Celery)

4. Показывает: "Agar email ro'yxatdan o'tgan bo'lsa, havola yuboramiz"
   (не раскрывает существует ли email — security)

5. Открыть email
   └─> Нажать на reset link
       └─> /password-reset/confirm?token=xyz123

6. Ввести новый пароль
   ├─ Новый пароль: NewSecure456
   └─ Подтвердить: NewSecure456

7. Backend: POST /api/v1/identity/auth/password-reset/confirm/
   ├─ Проверяет token валиден
   ├─ Обновляет password
   └─> Отменяет ВСЕ refresh tokens (force logout everywhere)

8. Показывает: "Parol yangilandi!"
   └─> Редирект на /login

9. Войти с новым паролем
   └─> Продолжает обучение
```

---



```
1. Студент на /login
   └─> Не помнит точный пароль, пробует варианты

2. Попытка 1: Wrong123 → ❌ "Email yoki parol noto'g'ri."
3. Попытка 2: Wrong456 → ❌ "Email yoki parol noto'g'ri."
4. Попытка 3: Wrong789 → ❌ "Email yoki parol noto'g'ri."
5. Попытка 4: WrongABC → ❌ "Email yoki parol noto'g'ri."
6. Попытка 5: WrongXYZ → ❌ "Email yoki parol noto'g'ri."

7. Попытка 6: Correct123 → ❌ Locked!
   └─> Error: "Hisob vaqtincha bloklangan (5 marta noto'g'ri parol). 15 daqiqadan keyin qayta urinib ko'ring."

8. Показывает lockout message с временем

9. Студент ждёт 15 минут
   (ИЛИ использует password reset — обходит lockout)

10. Через 15 минут: lockout снят автоматически
    └─> Может войти снова
```

---



```
1-14. Как Сценарий 1, но выбирает delivery_format: "offline"

15. Backend создаёт CourseEnrollment(delivery_format="offline")
    └─> Mentorship Domain:
        └─> Назначает студента в MentorGroup
            └─> Создаёт Attendance записи для будущих занятий

16. Студент видит schedule в dashboard
    └─> /dashboard/student
        └─> "Offline darslar jadvali"
            ├─ Дата: 2026-06-20, 10:00
            ├─ Ментор: Rustam Aliyev
            └─> Место: Online Zoom / Office

17. Студент посещает занятие
    └─> Ментор отмечает attendance
        └─> Backend: POST /api/v1/mentorship/attendance/
            ├─ student_id
            ├─ session_id
            └─ status: "present"

18. После занятия: ментор даёт homework assignment
    └─> Submissions Domain:
        └─> Assignment создаётся для урока
            ├─ lesson_id
            ├─ submission_type: "file" / "github" / etc.
            └─ deadline_offset_days: 7

19. Студент видит homework в lesson page
    └─> /courses/python/lessons/{id}
        └─> Assignment section:
            ├─> "📝 Assignment: Python basics homework"
            └─> Кнопка "Boshlash"

20. Начать homework
    └─> /assignments/{id}/submit
        └─> SubmissionForm
            ├─ GitHub (link)
            ├─ File upload (S3)
            ├─ Text (editor)
            └─ Link (URL)

21. Выбрать File upload
    └─> FileUploadZone
        └─> Перетаскивает homework.zip

22. Upload файла
    └─> Frontend:
        ├─ POST /api/v1/submissions/uploads/presigned-url/
        │   └─> Получает presigned URL
        ├─> Upload файл напрямую к S3
        │   └─> Progress bar: 0% → 30% → 100%
        └─> POST /api/v1/submissions/submissions/{id}/revisions/
            ├─ s3_key: "submissions/user123/uuid/homework.zip"
            ├─ submission_type: "file"
            └─> Создаёт SubmissionRevision

23. Submission отправлен
    └─> Backend:
        └─> Submission.status = "under_review"
            └─> Событие: SubmissionSubmitted (Outbox)

24. Событие → добавляет в mentor work queue
    └─> Mentorship Domain:
        └─> MentorWorkQueue.pending_submissions += 1

25. Ментор видит в dashboard
    └─> /dashboard/mentor/submissions
        └─> Список pending submissions
            └─> Нажимает на submission

26. Ментор review
    └─> /dashboard/mentor/submissions/{id}
        ├─ Скачивает файл (presigned download URL)
        ├─ Проверяет код
        └─> Оставляет feedback:
            ├─ Score: 85 / 100
            ├─ Status: "approved" / "changes_requested"
            └─ Feedback: "Good work! Fix line 42..."

27. Backend: POST /api/v1/submissions/reviews/
    └─> Создаёт Review
        └─> Submission.status = "approved"
            └─> Событие: SubmissionReviewed (Outbox)

28. Студент получает notification
    └─> Email: "Vazifangiz tekshirildi!"
    └─> Dashboard badge: "🔔 Yangi feedback"

29. Студент смотрит feedback
    └─> /submissions/{id}
        ├─ Score: 85 / 100
        ├─ Status: ✅ Approved
        └─> Mentor comment

30. Если "changes_requested":
    └─> Студент может resubmit
        └─> Повторить шаги 20-29
```

---



```
24-26. Как Сценарий 1, но assessment содержит coding question

27. Отвечает на coding question
    └─> Code editor in browser
        └─> Пишет код:
            ```python
            def sum_numbers(a, b):
                return a + b
            ```

28. Submit код
    └─> Backend: POST /api/v1/assessment/attempts/{id}/responses/
        ├─ item_id
        └─ submitted_code: "def sum_numbers..."
            └─> Assessment Domain:
                └─> Создаёт AssessmentResponse
                    └─> Событие: CodingSubmitted (Outbox)

29. Событие → запускает auto-check
    └─> Submissions Domain:
        └─> Celery task: run_code_execution
            ├─ Создаёт sandbox (Docker)
            ├─ Запускает код с test cases
            ├─ Проверяет output
            └─> Сохраняет results:
                ├─ Test 1: ✅ Pass
                ├─ Test 2: ✅ Pass
                └─ Test 3: ❌ Fail (expected 5, got 3)

30. Auto-check завершён
    └─> AssessmentResponse.auto_check_result:
        ├─ tests_passed: 2 / 3
        ├─ auto_score: 66 / 100
        └─> status: "pending_review" (requires mentor)

31. Ментор review coding answer
    └─> Может override auto_score
        └─> mentor_points: 80 / 100
            └─> feedback: "Логика правильная, но edge case..."

32. Финальный score = mentor_points (если есть) ИЛИ auto_score
```

---



```
31-32. Как Сценарий 1 (завершил курс, получил сертификат)

33. Студент хочет поделиться сертификатом
    └─> /certificates/{id}
        ├─ Скачать PDF
        ├─ Verification code: AB12CD
        └─> Share link: learnflow.uz/verify/AB12CD

34. Студент добавляет сертификат в LinkedIn
    ├─ Upload PDF
    └─ Добавляет verification link

35. Работодатель видит LinkedIn
    └─> Хочет проверить сертификат подлинный

36. Открывает learnflow.uz/verify/AB12CD
    └─> Public Certificate Verification Page
        ├─ Student name: Alisher Umarov
        ├─ Course: Python для начинающих
        ├─ Issue date: 2026-06-15
        ├─ Status: ✅ Valid
        └─> QR code для быстрой проверки

37. Работодатель убедился: сертификат подлинный
```

---



```
1-5. Как Сценарий 1 (регистрация)

6. Студент ждёт 5 минут → email не пришёл

7. На /verify-email странице
   └─> Нажимает "Emailni qayta yuboring"

8. Backend: POST /api/v1/identity/auth/verify-email/resend/
   ├─ Проверяет cooldown (120 секунд)
   └─> Генерирует НОВЫЙ token
       └─> Отправляет новый email

9. Показывает: "✅ Email qayta yuborildi!"
   └─> Countdown: 120s → 119s → ... → 0s

10. Кнопка disabled 120 секунд
    └─> Предотвращает spam

11. Студент проверяет почту или Spam папку
    └─> Находит email там!
        └─> Верифицирует успешно
```

---




- `/api/v1/identity/auth/login/`
- `/api/v1/identity/auth/logout/`
- `/api/v1/identity/auth/logout/all/`
- `/api/v1/identity/auth/register/`
- `/api/v1/identity/auth/token/refresh/`
- `/api/v1/identity/auth/verify-email/`
- `/api/v1/identity/auth/verify-email/resend/`
- `/api/v1/identity/auth/password-reset/`
- `/api/v1/identity/auth/password-reset/confirm/`
- `/api/v1/identity/profile/me/`
- `/api/v1/identity/profile/me/`
- `/api/v1/identity/profile/me/password/`
- `/api/v1/identity/profile/me/settings/`
- `/api/v1/identity/profile/me/settings/`
- `/api/v1/identity/profile/me/sessions/`
- `/api/v1/identity/profile/me/sessions/{session_id}/`


- `GET /api/v1/learning/courses/` (catalog)
- `GET /api/v1/learning/courses/{id}/` (detail)
- `GET /api/v1/learning/courses/{id}/modules/`
- `GET /api/v1/learning/modules/{id}/lessons/`
- `GET /api/v1/learning/lessons/{id}/`
- `GET /api/v1/learning/lessons/{id}/content/`


- `POST /api/v1/enrollment/enroll/`
- `GET /api/v1/enrollment/my-enrollments/`
- `GET /api/v1/enrollment/enrollments/{id}/`


- `GET /api/v1/progress/course/{enrollment_id}/`
- `GET /api/v1/progress/module/{enrollment_id}/{module_id}/`
- `GET /api/v1/progress/lesson/{enrollment_id}/{lesson_id}/`
- `POST /api/v1/progress/content-view/`


- `GET /api/v1/assessment/modules/{module_id}/`
- `GET /api/v1/assessment/assessments/{id}/`
- `POST /api/v1/assessment/attempts/`
- `GET /api/v1/assessment/attempts/{id}/`
- `POST /api/v1/assessment/attempts/{id}/responses/`
- `POST /api/v1/assessment/attempts/{id}/finalize/`


- `GET /api/v1/submissions/assignments/by-lesson/{lesson_id}/`
- `GET /api/v1/submissions/assignments/{id}/`
- `POST /api/v1/submissions/submissions/`
- `GET /api/v1/submissions/submissions/{id}/`
- `GET /api/v1/submissions/submissions/my/`
- `POST /api/v1/submissions/submissions/{id}/revisions/`
- `POST /api/v1/submissions/uploads/presigned-url/`
- `GET /api/v1/submissions/uploads/download-url/{file_id}/`


- `GET /api/v1/certificates/my/`
- `GET /api/v1/certificates/{id}/`
- `GET /api/v1/certificates/verify/{code}/` (public)

---




```
POST /register → 400 Bad Request
Error: "Bu email allaqachon ro'yxatdan o'tgan va tasdiqlangan."
```


```
GET /verify-email?token=expired → 400 Bad Request
Error: "Havola noto'g'ri yoki muddati tugagan."
→ Решение: resend verification email
```


```
POST /login → 401 Unauthorized
Error: "Email tasdiqlanmagan. Pochta qutingizni tekshiring."
```


```
POST /attempts/{id}/finalize/ → 400 Bad Request
Error: "Vaqt tugadi. Attempt avtomatik yakunlandi."
→ Backend автоматически finalize с текущими ответами
```


```
Frontend validation → Error: "Fayl hajmi 100MB dan oshmasligi kerak."
→ Не отправляет на backend
```


```
Frontend: следующий модуль disabled
Backend: 403 Forbidden если попытается обойти
Error: "Oldingi modulni tugallang."
```

---



1. ✅ Registration (with email verification)
2. ✅ Login (with lockout protection)
3. ✅ Course enrollment (online/offline)
4. ✅ Learning content (video, text, materials)
5. ✅ Progress tracking (automatic)
6. ✅ Module assessments (quiz, essay, coding)
7. ✅ Homework submissions (GitHub, file, text, link)
8. ✅ File upload (S3 presigned URLs)
9. ✅ Mentor feedback (reviews, scores)
10. ✅ Course completion
11. ✅ Certificate generation
12. ✅ Certificate verification (public)

**All MVP flows работают!** 🎉
