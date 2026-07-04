

**СУБД:** PostgreSQL 16  
**UUID PK:** `gen_random_uuid()` везде  
**Timestamps:** `TIMESTAMPTZ` (всегда с таймзоной)  
**Soft delete:** `deleted_at TIMESTAMPTZ NULLABLE` (не hard delete)

---



```
Таблица:     {app}_{model}            → courses_course
Индекс:      idx_{table}_{fields}     → idx_course_status
Уникальный:  uq_{table}_{fields}      → uq_enrollment_user_course
Constraint:  chk_{table}_{rule}       → chk_course_status
FK:          {field}_id               → enrollment_id, course_id
```

---




| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| name | VARCHAR(100) | Отображаемое название |
| slug | VARCHAR(100) UNIQUE | URL-safe, неизменяемый |
| parent_id | UUID FK NULLABLE | Self-ref. NULL = корневая категория. Max глубина = 2 |
| description | VARCHAR(500) NULLABLE | |
| icon | VARCHAR(50) NULLABLE | Heroicons id или emoji |
| order | SMALLINT DEFAULT 0 | Порядок в списке |
| is_active | BOOLEAN DEFAULT TRUE | |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| title | VARCHAR(255) NOT NULL | |
| slug | VARCHAR(255) UNIQUE NOT NULL | Неизменяем после публикации |
| description | TEXT NULLABLE | Markdown |
| short_description | VARCHAR(500) NULLABLE | Для карточек каталога |
| thumbnail_url | TEXT NULLABLE | S3/CDN URL |
| category_id | UUID FK NULLABLE | → courses_coursecategory, SET NULL |
| status | VARCHAR(20) | draft / published / archived |
| supports_online | BOOLEAN DEFAULT TRUE | Курс поддерживает online |
| supports_offline | BOOLEAN DEFAULT FALSE | Курс поддерживает offline |
| language | VARCHAR(10) DEFAULT 'ru' | BCP-47 |
| estimated_weeks | SMALLINT NULLABLE | |
| is_sequential | BOOLEAN DEFAULT TRUE | Модули проходить по порядку |
| created_by_id | FK → accounts_user | SET NULL при удалении |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | Soft delete |

**Constraints:** `supports_online OR supports_offline = TRUE`, status IN (draft/published/archived)


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| course_id | UUID FK NOT NULL | → courses_course, CASCADE |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| order | SMALLINT NOT NULL | Уникален внутри курса |
| is_published | BOOLEAN DEFAULT FALSE | |
| estimated_hours | SMALLINT NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(course_id, order)` WHERE deleted_at IS NULL


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| module_id | UUID FK NOT NULL | → courses_module, CASCADE |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| order | SMALLINT NOT NULL | Уникален внутри модуля |
| is_published | BOOLEAN DEFAULT FALSE | |
| is_free_preview | BOOLEAN DEFAULT FALSE | Доступен без записи |
| estimated_minutes | SMALLINT NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK NOT NULL | → courses_lesson, CASCADE |
| type | VARCHAR(20) | video/pdf/slides/text/link/recording/code |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| url | TEXT NULLABLE | Для video/pdf/slides/link/recording |
| body | TEXT NULLABLE | Для text/code |
| order | SMALLINT NOT NULL | |
| duration_seconds | INT NULLABLE | Только для video/recording |
| file_size_bytes | BIGINT NULLABLE | |
| is_required | BOOLEAN DEFAULT TRUE | Учитывается в content gate |
| is_downloadable | BOOLEAN DEFAULT FALSE | |
| metadata | JSONB DEFAULT '{}' | Доп. данные по типу |



> ⚠️ **DEPRECATED (ADR-014):** Эта таблица будет заменена на `submissions_assignment`.  
> Новый код должен использовать Submissions Domain.  
> Сохранена в документации для контекста миграции.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK UNIQUE | 1:1 с уроком |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NOT NULL | |
| max_score | SMALLINT DEFAULT 100 | |
| deadline_offset_days | SMALLINT NULLABLE | Дней от enrolledAt |
| submission_type | VARCHAR(20) | file/text/link/code |
| allowed_file_types | VARCHAR(200) NULLABLE | .pdf,.docx и т.д. |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | FK → accounts_user | PROTECT |
| course_id | FK → courses_course | RESTRICT (не удалить с active enrollments) |
| status | VARCHAR(20) | active / completed / dropped |
| delivery_format | VARCHAR(10) | online / offline |
| enrolled_at | TIMESTAMPTZ NOT NULL | |
| completed_at | TIMESTAMPTZ NULLABLE | |
| dropped_at | TIMESTAMPTZ NULLABLE | |
| enrolled_by_id | FK NULLABLE → accounts_user | SET NULL |

**Index:** UNIQUE `(user_id, course_id)`

---




| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK UNIQUE | 1:1 с enrollment |
| course_id | UUID (denorm) | Из enrollment |
| user_id | UUID (denorm) | Из enrollment |
| delivery_format | VARCHAR(10) | Snapshot из enrollment |
| is_sequential | BOOLEAN | Snapshot из course |
| status | VARCHAR(20) | not_started / in_progress / completed |
| total_modules_count | SMALLINT | Snapshot |
| completed_modules_count | SMALLINT | Инкрементируется через F() |
| cached_percentage | SMALLINT DEFAULT 0 | Лениво обновляется |
| started_at / completed_at / last_activity_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK | |
| module_id | FK → courses_module | |
| course_id | UUID (denorm) | |
| module_order | SMALLINT | Snapshot |
| status | VARCHAR(25) | locked/unlocked/in_progress/assessment_pending/completed |
| total_lessons_count | SMALLINT | Snapshot |
| completed_lessons_count | SMALLINT | F() increment |
| assessment_required | BOOLEAN | Snapshot из Assessment Domain |
| assessment_passed | BOOLEAN DEFAULT FALSE | |
| assessment_passed_at | TIMESTAMPTZ NULLABLE | |
| is_stale | BOOLEAN DEFAULT FALSE | Модуль удалён |
| unlocked_at / completed_at / last_activity_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK | |
| lesson_id | FK → courses_lesson | |
| module_id | UUID (denorm) | |
| course_id | UUID (denorm) | |
| lesson_order | SMALLINT | Snapshot |
| module_order | SMALLINT | Snapshot — критично для get_next_action |
| status | VARCHAR(20) | locked/unlocked/in_progress/completed |
| completion_source | VARCHAR(30) NULLABLE | student_activity/mentor_attendance/admin_override |
| required_content_count | SMALLINT DEFAULT 0 | Snapshot. WHERE status!='completed' при обновлении |
| viewed_required_count | SMALLINT DEFAULT 0 | F() increment only |
| homework_required | BOOLEAN DEFAULT FALSE | Snapshot |
| homework_submitted | BOOLEAN DEFAULT FALSE | |
| homework_submitted_at | TIMESTAMPTZ NULLABLE | |
| is_stale | BOOLEAN DEFAULT FALSE | Урок удалён |
| is_active | BOOLEAN DEFAULT TRUE | FALSE при drop enrollment |
| override_by_id | UUID NULLABLE | Аудит admin override |
| override_reason | TEXT NULLABLE | |
| unlocked_at / started_at / completed_at | TIMESTAMPTZ NULLABLE | |

**Critical index:** `(enrollment_id, module_order, lesson_order)` WHERE status IN ('unlocked','in_progress') AND is_stale=FALSE AND is_active=TRUE


| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK → courses_courseenrollment | CASCADE |
| content_id | UUID (soft ref, NO FK) | Content может быть удалён |
| lesson_progress_id | FK → progress_lessonprogress | CASCADE |
| is_required | BOOLEAN | Snapshot при просмотре |
| first_viewed_at / last_viewed_at | TIMESTAMPTZ | |
| view_count | SMALLINT DEFAULT 1 | |
| last_position_seconds | INT NULLABLE | Для video resume |
| total_duration_seconds | INT NULLABLE | Snapshot для watch threshold |

**Index:** UNIQUE `(enrollment_id, content_id)`

---



**Изменения:** Assessment = контейнер без поля type. Состав определяется через items. Добавлен type=interview. Mentor override с историей изменений.


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| module_id | UUID FK → courses_module | UNIQUE — один assessment на модуль |
| title | VARCHAR(255) NOT NULL | |
| instructions | TEXT NULLABLE | |
| passing_percentage | DECIMAL(5,2) | 0–100. Процент для зачёта (было passing_score) |
| max_attempts | SMALLINT NULLABLE | NULL = unlimited |
| time_limit_minutes | SMALLINT NULLABLE | NULL = без ограничений |
| shuffle_items | BOOLEAN DEFAULT FALSE | |
| is_published | BOOLEAN DEFAULT FALSE | |
| created_by_id | FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assessment_id | FK | |
| type | VARCHAR(20) | single_choice/multiple_choice/text_answer/coding/project/interview |
| order | SMALLINT | |
| title | TEXT NOT NULL | Текст вопроса/задания |
| description | TEXT NULLABLE | Дополнительный контекст |
| max_points | DECIMAL(6,2) | |
| partial_credit_strategy | VARCHAR(20) DEFAULT 'all_or_nothing' | all_or_nothing / proportional |
| explanation | TEXT NULLABLE | Показывается после оценки |
| mentor_review_required | BOOLEAN DEFAULT FALSE | TRUE для text_answer/project/interview |
| coding_language | VARCHAR(30) NULLABLE | Только для type=coding |
| starter_code | TEXT NULLABLE | Только для type=coding |
| sample_answer | TEXT NULLABLE | Для ментора (text_answer) |
| min_word_count | SMALLINT NULLABLE | Только для type=text_answer |
| submission_requirements | TEXT NULLABLE | Только для type=project |


| Поле | Тип | Описание |
|------|-----|----------|
| item_id | FK → assessment_assessmentitem | |
| text | TEXT NOT NULL | |
| is_correct | BOOLEAN NOT NULL | |
| order | SMALLINT | |
| explanation | TEXT NULLABLE | Per-option объяснение |


| Поле | Тип | Описание |
|------|-----|----------|
| item_id | FK → assessment_assessmentitem | |
| input | TEXT NOT NULL | stdin или аргументы |
| expected_output | TEXT NOT NULL | |
| points | DECIMAL(5,2) NULLABLE | NULL = equal share of item's max_points |
| time_limit_ms | INT DEFAULT 2000 | |
| memory_limit_mb | INT DEFAULT 128 | |
| is_hidden | BOOLEAN DEFAULT FALSE | Скрыт от студента |
| is_sample | BOOLEAN DEFAULT FALSE | Показывается в условии |
| order | SMALLINT | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| enrollment_id | FK → courses_courseenrollment | |
| assessment_id | FK → assessment_moduleassessment | |
| user_id | UUID (denorm) | |
| attempt_number | SMALLINT | 1, 2, 3... |
| grading_status | VARCHAR(20) | pending/auto_graded/mentor_review/finalized |
| started_at | TIMESTAMPTZ | |
| submitted_at | TIMESTAMPTZ NULLABLE | |
| graded_at | TIMESTAMPTZ NULLABLE | Когда finalized |
| expires_at | TIMESTAMPTZ NULLABLE | |
| max_score | DECIMAL(8,2) | Snapshot при создании |
| final_score | DECIMAL(8,2) NULLABLE | Сумма final_points из responses |
| percentage | DECIMAL(5,2) NULLABLE | final_score / max_score * 100 |
| passed | BOOLEAN NULLABLE | percentage >= passing_percentage |
| mentor_note | TEXT NULLABLE | Общий комментарий ментора |

**Index:** UNIQUE `(enrollment_id, assessment_id, attempt_number)`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| attempt_id | FK → assessment_assessmentattempt | |
| item_id | FK → assessment_assessmentitem | |
| selected_option_ids | UUID[] | Для choice-типов |
| text_response | TEXT NULLABLE | Для text_answer/interview |
| submitted_code | TEXT NULLABLE | Для coding |
| coding_language | VARCHAR(30) NULLABLE | Для coding |
| submission_id | UUID NULLABLE (soft ref) | Для project → Submissions Domain |
| is_graded | BOOLEAN DEFAULT FALSE | |
| auto_points | DECIMAL(6,2) NULLABLE | Авто-оценка |
| mentor_points | DECIMAL(6,2) NULLABLE | Ментор override |
| final_points | DECIMAL(6,2) NULLABLE | COALESCE(mentor_points, auto_points) |
| is_correct | BOOLEAN NULLABLE | Для choice items |
| reviewed_by_id | UUID FK NULLABLE | → accounts_user (ментор) |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| review_comment | TEXT NULLABLE | Почему изменил балл |

**Index:** UNIQUE `(attempt_id, item_id)`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| response_id | FK → assessment_assessmentresponse | |
| test_case_id | FK → assessment_codingtestcase | |
| passed | BOOLEAN NOT NULL | |
| actual_output | TEXT NULLABLE | |
| execution_time_ms | INT NULLABLE | |
| memory_used_mb | INT NULLABLE | |
| error_message | TEXT NULLABLE | |
| points_earned | DECIMAL(5,2) | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| response_id | FK → assessment_assessmentresponse | |
| attempt_id | UUID (denorm) | Для быстрых запросов |
| old_score | DECIMAL(6,2) | До изменения |
| new_score | DECIMAL(6,2) | После изменения |
| mentor_id | UUID FK → accounts_user | |
| reason | TEXT | Почему изменил |
| created_at | TIMESTAMPTZ | |

---



**Концепция:** Assignment (описание задания) отделено от Submission (попытка выполнения). Версионирование через SubmissionRevision.


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK NULLABLE | → courses_lesson (SET NULL) |
| assessment_item_id | UUID NULLABLE | Soft ref на assessment_assessmentitem |
| type | VARCHAR(20) | theory / coding / project |
| title | VARCHAR(255) | |
| description | TEXT | Markdown |
| max_score | DECIMAL(6,2) | |
| deadline_offset_days | SMALLINT NULLABLE | Дней от enrolledAt |
| submission_types_allowed | VARCHAR(100)[] | ['github_repository', 'file_upload'] |
| allowed_file_extensions | VARCHAR(200) NULLABLE | .pdf,.zip,.docx |
| max_file_size_mb | SMALLINT DEFAULT 50 | |
| auto_check_enabled | BOOLEAN DEFAULT FALSE | |
| auto_check_config | JSONB NULLABLE | Конфиг для автопроверки |
| created_by_id | UUID FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `type IN ('theory', 'coding', 'project')`, CHECK `lesson_id IS NOT NULL OR assessment_item_id IS NOT NULL`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assignment_id | UUID FK → submissions_assignment | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| student_id | UUID (denorm) | |
| status | VARCHAR(20) | draft/submitted/under_review/changes_requested/approved/rejected |
| current_revision_number | SMALLINT DEFAULT 0 | |
| final_score | DECIMAL(6,2) NULLABLE | Финальная оценка |
| created_at | TIMESTAMPTZ | |
| first_submitted_at | TIMESTAMPTZ NULLABLE | |
| last_submitted_at | TIMESTAMPTZ NULLABLE | |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| deadline | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(enrollment_id, assignment_id)`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK → submissions_submission (CASCADE) | |
| revision_number | SMALLINT | 1, 2, 3... |
| submission_type | VARCHAR(20) | github_repository/file_upload/text_answer/external_link |
| payload | JSONB | Зависит от submission_type |
| notes | TEXT NULLABLE | Комментарий студента |
| submitted_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_number)`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK → submissions_submissionrevision (CASCADE) | |
| file_name | VARCHAR(255) | |
| file_size_bytes | BIGINT | |
| mime_type | VARCHAR(100) | |
| storage_path | TEXT | S3 path |
| scan_status | VARCHAR(20) | pending/running/passed/failed |
| scan_result | JSONB NULLABLE | Результат ClamAV |
| scanned_at | TIMESTAMPTZ NULLABLE | |
| uploaded_at | TIMESTAMPTZ | |

**Constraints:** CHECK `scan_status IN ('pending', 'running', 'passed', 'failed')`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK → submissions_submissionrevision | |
| check_type | VARCHAR(30) | tests/linting/coverage/docker_build |
| status | VARCHAR(20) | pending/running/passed/failed/error |
| score | DECIMAL(6,2) NULLABLE | |
| report | JSONB | Детальный отчёт |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK → submissions_submission | |
| revision_id | UUID FK → submissions_submissionrevision | |
| mentor_id | UUID FK → accounts_user | |
| score | DECIMAL(6,2) | |
| max_score | DECIMAL(6,2) | Snapshot |
| feedback | TEXT | |
| status | VARCHAR(20) | changes_requested/approved/rejected |
| reviewed_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_id)`

---



**Концепция:** Группы студентов с ментором. Offline занятия с гибким расписанием. Attendance отмечается ментором вручную.


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK → accounts_user | |
| course_id | UUID FK → courses_course | |
| name | VARCHAR(255) | "Python Backend 
| planned_lessons_count | SMALLINT | План: 12 занятий |
| max_students | SMALLINT DEFAULT 30 | |
| current_students_count | SMALLINT DEFAULT 0 | F() increment |
| status | VARCHAR(20) | active/completed/archived |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `status IN ('active', 'completed', 'archived')`, CHECK `current_students_count <= max_students`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK → accounts_user | |
| group_id | UUID FK → mentorship_mentorgroup (CASCADE) | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| joined_at | TIMESTAMPTZ | |
| left_at | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(student_id, group_id)`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| group_id | UUID FK → mentorship_mentorgroup | |
| lesson_id | UUID FK NULLABLE → courses_lesson (SET NULL) | |
| module_id | UUID (denorm) | |
| title | VARCHAR(255) | "Занятие 5: Django ORM" |
| description | TEXT NULLABLE | |
| scheduled_start | TIMESTAMPTZ | |
| scheduled_end | TIMESTAMPTZ | |
| actual_start | TIMESTAMPTZ NULLABLE | |
| actual_end | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | scheduled/in_progress/completed/cancelled/rescheduled |
| location | VARCHAR(255) NULLABLE | "Room 301" |
| meeting_url | TEXT NULLABLE | Zoom/Google Meet |
| notes | TEXT NULLABLE | Заметки ментора |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled')`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| session_id | UUID FK → mentorship_offlinesession | |
| student_id | UUID FK → accounts_user | |
| status | VARCHAR(20) | present/absent/late/excused |
| marked_by_id | UUID FK → accounts_user | Ментор |
| marked_at | TIMESTAMPTZ | |
| notes | TEXT NULLABLE | |

**Index:** UNIQUE `(session_id, student_id)`  
**Constraints:** CHECK `status IN ('present', 'absent', 'late', 'excused')`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK → accounts_user | |
| entered_at | TIMESTAMPTZ | |
| exited_at | TIMESTAMPTZ NULLABLE | |
| source | VARCHAR(20) | face_id/turnstile/manual |
| device_id | VARCHAR(100) NULLABLE | |
| location | VARCHAR(100) NULLABLE | |
| metadata | JSONB | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK → accounts_user | |
| item_type | VARCHAR(20) | submission/assessment_attempt |
| item_id | UUID | ID submission или attempt |
| student_id | UUID | |
| student_name | VARCHAR(255) (denorm) | |
| title | VARCHAR(255) | |
| submitted_at | TIMESTAMPTZ | |
| deadline | TIMESTAMPTZ NULLABLE | |
| is_overdue | BOOLEAN | |
| status | VARCHAR(20) | pending/in_review/completed |
| created_at / updated_at | TIMESTAMPTZ | |

---



**Концепция:** Сертификат = snapshot данных на момент выдачи. PDF генерируется async. Публичная верификация через verification_code.


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| name | VARCHAR(255) | "Backend Certificate Template" |
| description | TEXT NULLABLE | |
| background_image | TEXT | S3 URL |
| pdf_template | TEXT | Path к Jinja2 template |
| font_config | JSONB | Шрифты, размеры, цвета |
| layout_config | JSONB | Позиции элементов |
| is_active | BOOLEAN DEFAULT TRUE | |
| created_by_id | UUID FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK → accounts_user (PROTECT) | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| course_id | UUID (denorm) | |
| template_id | UUID FK → certificates_certificatetemplate | |
| certificate_number | VARCHAR(50) UNIQUE | "LF-2026-8AF3D2" |
| verification_code | VARCHAR(50) UNIQUE | То же что certificate_number |
| student_full_name_snapshot | VARCHAR(255) | Snapshot |
| course_name_snapshot | VARCHAR(255) | Snapshot |
| course_description_snapshot | TEXT NULLABLE | Snapshot |
| final_score | DECIMAL(6,2) NULLABLE | |
| completion_date | DATE | |
| issued_at | TIMESTAMPTZ | |
| pdf_url | TEXT NULLABLE | S3 URL |
| pdf_generated_at | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | pending/issued/revoked |
| revoked_at | TIMESTAMPTZ NULLABLE | |
| revoked_by_id | UUID FK NULLABLE → accounts_user | |
| revoked_reason | TEXT NULLABLE | |
| metadata | JSONB | |

**Constraints:** CHECK `status IN ('pending', 'issued', 'revoked')`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK → certificates_certificate | |
| reason | TEXT | |
| requested_by_id | UUID FK → accounts_user | |
| requested_at | TIMESTAMPTZ | |
| status | VARCHAR(20) | pending/approved/rejected |
| reviewed_by_id | UUID FK NULLABLE → accounts_user | |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| new_certificate_id | UUID FK NULLABLE → certificates_certificate | |

**Constraints:** CHECK `status IN ('pending', 'approved', 'rejected')`


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK → certificates_certificate | |
| action | VARCHAR(50) | created/issued/revoked/reissued/downloaded |
| actor_id | UUID FK NULLABLE → accounts_user | |
| details | JSONB | |
| ip_address | INET NULLABLE | |
| created_at | TIMESTAMPTZ | |

---





**Концепция:** Outbox Pattern для критичных событий с гарантированной доставкой (at-least-once). См. ADR-029.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| event_type | VARCHAR(100) | StudentEnrolled, CourseCompleted, SubmissionReviewed, etc. |
| aggregate_id | UUID | enrollment_id, submission_id, certificate_id (для группировки) |
| payload | JSONB | Полный payload события (dataclass → dict) |
| occurred_at | TIMESTAMPTZ | Когда событие произошло (auto_now_add) |
| processed_at | TIMESTAMPTZ NULLABLE | Когда было обработано (NULL = unprocessed) |
| retry_count | INTEGER DEFAULT 0 | Количество попыток обработки |
| last_error | TEXT NULLABLE | Последняя ошибка при обработке |

**Индексы:**
- `idx_outbox_processing` на `(processed_at, occurred_at)` — для worker выборки
- `idx_outbox_event_type` на `event_type` — для мониторинга
- `idx_outbox_aggregate` на `(event_type, aggregate_id)` — для debug/audit

**Критичные события (используют Outbox):**
1. `StudentEnrolled` → создаёт CourseProgress
2. `CourseCompleted` → генерирует Certificate
3. `SubmissionReviewed` → обновляет баллы AssessmentResponse
4. `CertificateIssued` → отправка email
5. `AssessmentAttemptStarted` (project) → создаёт Assignment

**Обработка:** Celery Beat task каждые 10 секунд (`shared.tasks.process_outbox_events`)

**Retention:** События старше 30 дней с `processed_at IS NOT NULL` архивируются (партиционирование или удаление).

---



1. **UUID везде** — никаких serial/integer PK
2. **Soft delete** — `deleted_at` вместо DELETE для Course, Module, Lesson
3. **Snapshot denormalization** — progress domain хранит снапшоты order/count из Learning
4. **NO DB FK через домены** — кроме `→ accounts_user` и внутри домена
5. **F() expressions** — все инкременты счётчиков
6. **Partial indexes** — `WHERE deleted_at IS NULL`, `WHERE status != 'completed'`
