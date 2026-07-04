



LearnFlow — образовательная экосистема для профессиональных IT-курсов.  
Платформа объединяет структурированный контент, персональных менторов и систему оценки прогресса.

---




- Студент проходит уроки в удобное время
- Ментор назначен, но не проводит живые сессии
- Студент сам открывает контент, просматривает, сдаёт задания
- Прогресс: `completion_source = student_activity`


- Ментор ведёт группу (`MentorGroup`) по расписанию
- Проводятся живые сессии (`OfflineSession`) по конкретным урокам
- Ментор отмечает посещаемость → прогресс студента обновляется
- Прогресс: `completion_source = mentor_attendance`


**Один курс = один набор контента** для обоих форматов.  
"Python Backend" — один курс, разные способы прохождения.

---



```
Студент записывается на курс  (CourseEnrollment)
          ↓
    Изучает уроки               (LessonProgress: unlocked → in_progress → completed)
          ↓
    Просматривает контент       (LessonContentView: content gate)
          ↓
    Сдаёт домашнее задание     (HomeworkSubmission: homework gate)
          ↓
    Урок завершён              (LessonProgress: completed)
          ↓
    Следующий урок разблокирован (автоматически)
          ↓
    Все уроки модуля завершены
          ↓
    Сдаёт итоговый тест модуля  (ModuleAssessment → AssessmentAttempt)
          ↓
    Тест сдан                  (ModuleProgress: completed)
          ↓
    Следующий модуль разблокирован
          ↓
    Все модули завершены
          ↓
    Курс завершён → Сертификат  (Certificate)
```

---



```
Course (курс)
  └── Module (модуль, тематический блок)
       └── Lesson (урок)
            ├── LessonContent (видео, PDF, текст, код, ссылка...)
            ├── Assignment (задание — theory/coding/project, заменяет LessonHomework)
            ├── LessonPractice (практические задачи, опционально)
            └── LessonQuiz (мини-тест, опционально — НЕ блокирует прогресс)
       └── ModuleAssessment (итоговый тест модуля — блокирует следующий модуль)
```

**Важное разграничение:**
- `LessonQuiz` — учебный инструмент внутри урока. Не влияет на разблокировку.
- `ModuleAssessment` — итоговая оценка модуля. Блокирует переход к следующему.
- `Assignment` — домашнее задание или проект (заменяет старый LessonHomework).

---




- Записывается на курс
- Просматривает контент, сдаёт задания
- Проходит assessments
- Видит только опубликованный контент


- Ведёт offline группы
- Проверяет задания и text_answer в assessments
- Отмечает посещаемость
- Видит прогресс своих студентов
- **Не создаёт курсы**


- Создаёт и редактирует курсы, модули, уроки
- Публикует контент
- Видит черновики **своих** курсов
- **Не архивирует** — только Admin


- Полный доступ ко всему
- Архивирует и удаляет курсы
- Записывает студентов вручную
- Меняет delivery_format для enrolled студентов

---



| 
|---|---------|
| BR-01 | Нельзя записаться на неопубликованный курс |
| BR-02 | Нельзя записаться в offline если `course.supports_offline = FALSE` |
| BR-03 | Один студент — одна активная запись на курс (одновременно) |
| BR-04 | Урок завершён = терминальное состояние (нельзя отменить без admin/mentor override) |
| BR-05 | Модуль завершён только после прохождения всех уроков И assessment (если есть) |
| BR-06 | Публикация курса требует ≥1 опубликованного модуля с ≥1 опубликованным уроком |
| BR-07 | Удалить курс нельзя если есть хотя бы один enrolled студент (архивировать) |
| BR-08 | Для offline студентов посещаемость = выполнение контента (content gate bypass) |
| BR-09 | Homework gate (assignment) применяется всегда (и для online, и для offline студентов) |
| BR-10 | Assessment: pass/fail вычисляется только когда ВСЕ items оценены |
| BR-11 | Assessment = контейнер без type поля. Состав определяется через items |
| BR-12 | Mentor может пересмотреть авто-оценку. История изменений обязательна (audit trail) |
| BR-13 | Assignment заменяет LessonHomework. Типы: theory/coding/project |
| BR-14 | Студент может пересдать assignment. Версионирование через SubmissionRevision обязательно |
| BR-15 | Все загруженные файлы проходят ClamAV scan перед доступом ментора |
| BR-16 | AutoCheck (тесты, linting) отделён от SubmissionReview (ментор). Не смешивать |
| BR-17 | Только Admin назначает студентов в MentorGroup. Студент НЕ выбирает ментора |
| BR-18 | Attendance отмечается ментором вручную. Турникет = подсказка, не истина |
| BR-19 | Сертификат = snapshot данных на момент выдачи. Нельзя автоматически обновлять |
| BR-20 | PDF сертификата генерируется один раз (async) и сохраняется в S3 |

---





**Концепция:** Assignment (описание задания) отделено от Submission (попытка студента выполнить).

**Ключевые сущности:**
- `Assignment` — задание (theory/coding/project). Заменяет LessonHomework
- `Submission` — попытка студента выполнить assignment
- `SubmissionRevision` — версии попыток (студент пересдаёт после замечаний)
- `SubmissionFile` — загруженные файлы (с virus scan)
- `AutoCheck` — автоматические проверки (tests, linting, coverage)
- `SubmissionReview` — проверка ментора

**Типы submission:**
- `github_repository` — Backend/Frontend проекты (GitHub URL)
- `file_upload` — ZIP, PDF, PPTX, DOCX (дизайн, презентации)
- `text_answer` — Большие текстовые ответы
- `external_link` — Vercel, Render, Railway, YouTube, Figma

**Flow:**
1. Студент создаёт Submission для Assignment
2. Студент делает SubmissionRevision 1 (первая попытка)
3. Файлы проходят ClamAV scan → S3
4. AutoCheck запускается (если enabled)
5. Ментор проверяет → SubmissionReview (score, feedback, status)
6. Если `status=changes_requested` → студент делает SubmissionRevision 2
7. Ментор одобряет → `status=approved`
8. Событие `SubmissionApproved` → UserProgress (homework gate)

---



**Концепция:** Группы студентов с ментором. Offline занятия с гибким расписанием. Attendance отмечается вручную.

**Ключевые сущности:**
- `MentorGroup` — группа студентов с одним ментором
- `OfflineSession` — одно занятие группы (с гибким schedule)
- `Attendance` — посещаемость студента на занятии
- `AccessEvent` — события турникета (для аналитики, не для прогресса)
- `MentorWorkQueue` — очередь работ ментора (submissions + assessments)

**Правила:**
- Студент НЕ выбирает ментора — только Admin назначает
- Расписание динамическое — занятия можно отменять/переносить
- Ментор отмечает attendance вручную (турникет = подсказка)
- Attendance → событие `AttendanceMarked` → UserProgress → LessonCompleted (для offline)

**Flow:**
1. Admin создаёт MentorGroup (mentor + course + max_students)
2. Admin добавляет студентов в группу
3. Ментор создаёт OfflineSession (lesson + schedule)
4. На занятии ментор отмечает Attendance (bulk)
5. Событие `AttendanceMarked` → UserProgress
6. LessonProgress.status = 'completed' (completion_source = 'mentor_attendance')

---



**Концепция:** Сертификат = snapshot данных на момент выдачи. PDF генерируется async. Публичная verification.

**Ключевые сущности:**
- `CertificateTemplate` — шаблон PDF (layout, fonts, background)
- `Certificate` — выданный сертификат (snapshot данных)
- `CertificateReissueRequest` — запрос на переиздание
- `CertificateAuditLog` — история изменений

**Правила:**
- Сертификат — юридический документ. Snapshot данных (имя, курс) на момент выдачи
- PDF генерируется async через Celery (не блокирует CourseCompleted)
- PDF сохраняется в S3 один раз (не генерировать каждый раз)
- Публичная verification через `verification_code` (rate limiting)
- Revoke механизм (status = 'revoked')

**Flow:**
1. UserProgress → событие `CourseCompleted`
2. Certificates слушает → создаёт Certificate (status='pending')
3. Celery task: generate_certificate.delay()
4. PDF генерируется → upload S3 → status='issued'
5. Событие `CertificateIssued` → Notifications → email студенту
6. Публичная страница `/certificates/verify/{code}` доступна без auth

---



| Термин              | Определение |
|---------------------|-------------|
| Course              | Учебный курс. Верхний уровень контентной иерархии |
| Module              | Тематический блок внутри курса |
| Lesson              | Отдельный урок. Единица прогресса |
| LessonContent       | Материал урока (видео, PDF, текст и т.д.) |
| Assignment          | Задание (theory/coding/project). Заменяет LessonHomework |
| CourseEnrollment    | Запись студента на курс с указанием формата |
| delivery_format     | online или offline — способ прохождения курса |
| LessonProgress      | Состояние прогресса студента по уроку |
| ModuleAssessment    | Итоговый тест по модулю (без type поля, состав определяется items) |
| AssessmentAttempt   | Одна попытка прохождения assessment |
| AssessmentItem      | Один вопрос/задание в assessment (6 типов) |
| Submission          | Попытка студента выполнить assignment |
| SubmissionRevision  | Версия submission (студент пересдаёт после замечаний) |
| AutoCheck           | Автоматическая проверка (tests, linting, coverage) |
| SubmissionReview    | Проверка ментора |
| MentorGroup         | Группа студентов с одним ментором (offline) |
| OfflineSession      | Одно занятие группы (offline) |
| Attendance          | Посещаемость студента на занятии |
| AccessEvent         | Событие турникета (для аналитики) |
| MentorWorkQueue     | Очередь работ ментора (submissions + assessments) |
| Certificate         | Сертификат о завершении курса |
| CertificateTemplate | Шаблон PDF для сертификата |
| verification_code   | Уникальный код для публичной верификации сертификата |
| completion_source   | Источник завершения: student_activity / mentor_attendance / mentor_override / admin_override |
| content gate        | Условие: все required материалы просмотрены |
| homework gate       | Условие: задание (assignment) сдано |
| assessment gate     | Условие: итоговый тест модуля сдан |
