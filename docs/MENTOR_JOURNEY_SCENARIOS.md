

**Version:** MVP 95%  
**Date:** 2026-06-17  
**Language:** Uzbek (primary), Russian, English

---





```
1. Открыть learnflow.uz/login
   └─> Login Page

2. Войти как ментор
   ├─ Email: mentor@learnflow.uz
   └─ Parol: MentorPass123
       └─> Backend: POST /api/v1/identity/auth/login/
           ├─ Проверяет credentials
           ├─ Проверяет role: "mentor"
           ├─ Генерирует tokens
           └─> Возвращает access_token + refresh_token

3. Редирект на /dashboard/mentor
   └─> Mentor Dashboard
       ├─ Work Queue Overview:
       │   ├─ Pending Assessments: 5 ⏳
       │   ├─ Pending Submissions: 12 📝
       │   └─> Recent Activity
       ├─> My Students (если offline mentor)
       └─> Statistics (reviews completed today/week)

4. Просмотр Work Queue
   └─> Dashboard показывает:
       ├─ 🎯 Assessments needing review
       │   ├─ Python Quiz — Alisher Umarov (waiting 2 hours)
       │   ├─ Django Essay — Nodira Karimova (waiting 1 day)
       │   └─> Coding Task — Jasur Rahimov (waiting 3 hours)
       │
       └─ 📝 Submissions needing review
           ├─ Homework 
           ├─ Project — Malika Abdullayeva (waiting 2 days)
           └─> Lab Work — Otabek Nazarov (waiting 6 hours)

5. Нажать "Assessments" tab
   └─> /dashboard/mentor/assessments
       └─> Список pending assessments
           └─> Фильтры:
               ├─ By course
               ├─ By type (essay, coding)
               └─> By waiting time

6. Выбрать assessment для review
   └─> /dashboard/mentor/assessments/{attempt_id}
       └─> Assessment Review Page
           ├─ Student info:
           │   ├─ Name: Alisher Umarov
           │   ├─ Course: Python для начинающих
           │   └─> Enrollment: Online
           │
           ├─> Assessment info:
           │   ├─ Module: Basics
           │   ├─ Started: 2 hours ago
           │   ├─ Auto-graded: 45 / 60 (quiz)
           │   └─> Pending: Essay question (40 points)
           │
           └─> Responses:
               ├─ Q1-Q6: Quiz (auto-graded) ✅
               └─> Q7: Essay (needs review) ⏳

7. Review essay question
   └─> Essay Response:
       ├─ Question: "Explain the difference between list and tuple"
       ├─> Student answer: [300 words text]
       └─> Mentor actions:
           ├─ Read answer
           ├─ Assign points: 35 / 40
           └─> Write feedback: "Good explanation, but..."

8. Submit review
   └─> Backend: POST /api/v1/assessment/reviews/{response_id}/
       ├─ mentor_points: 35
       ├─ review_comment: "Good explanation..."
       └─> Assessment Domain:
           ├─> Обновляет AssessmentResponse
           ├─> Пересчитывает total_score: 80 / 100
           ├─> Устанавливает attempt.status = "passed"
           └─> Событие: AssessmentReviewed (Signal)

9. Событие → Notification студенту
   └─> Notifications Domain:
       └─> Email: "Testingiz baholandi!"
           └─> Student dashboard badge: 🔔

10. Ментор видит: "✅ Review submitted"
    └─> Редирект на /dashboard/mentor/assessments
        └─> Pending count: 5 → 4

11. Продолжить с submissions review
    └─> Нажать "Submissions" tab
        └─> /dashboard/mentor/submissions

12. Список pending submissions
    └─> Submissions Queue:
        ├─ Homework 
        ├─ Project — Malika (File upload)
        └─> Lab Work — Otabek (Text + Link)

13. Выбрать submission
    └─> /dashboard/mentor/submissions/{submission_id}
        └─> Submission Review Page
            ├─ Student: Shahzod Tursunov
            ├─ Assignment: "Python Homework 
            ├─ Lesson: "Variables and Data Types"
            ├─ Submitted: 4 hours ago
            ├─ Type: GitHub Repository
            └─> Link: github.com/shahzod/homework1

14. Просмотр работы (GitHub)
    └─> Ментор открывает GitHub link
        ├─> Смотрит код
        ├─> Проверяет README
        └─> Запускает локально (опционально)

15. Написать review
    └─> Review Form:
        ├─ Score: 90 / 100
        ├─ Status: [approved] / changes_requested / rejected
        └─> Feedback (text editor):
            ├─ "Отличная работа! ✅"
            ├─> "Но исправьте строку 42..."
            └─> "Добавьте unit tests"

16. Submit review
    └─> Backend: POST /api/v1/submissions/reviews/
        ├─ submission_id
        ├─ score: 90
        ├─ status: "approved"
        └─ feedback: "Отличная работа..."
            └─> Submissions Domain:
                ├─> Создаёт Review
                ├─> Submission.status = "approved"
                └─> Событие: SubmissionReviewed (Outbox)

17. Студент получает notification
    └─> Email + Dashboard badge
        └─> Студент видит feedback

18. Ментор продолжает работу
    └─> Pending submissions: 12 → 11
        └─> Повторить шаги 13-17
```

---



```
1-12. Как Сценарий 1

13. Выбрать submission с file upload
    └─> /dashboard/mentor/submissions/{id}
        └─> Submission Type: File Upload
            ├─ Student: Malika Abdullayeva
            ├─ Assignment: "Final Project"
            ├─ Files uploaded: 1
            └─> File: project.zip (15 MB)

14. Скачать файл
    └─> Нажать "Download" button
        └─> Frontend:
            └─> GET /api/v1/submissions/uploads/download-url/{file_id}/
                ├─> Backend проверяет: is_mentor = True
                ├─> Генерирует presigned download URL
                └─> Возвращает: {download_url, filename}

15. Browser автоматически скачивает
    └─> Direct download from S3
        └─> presigned URL (expires 1 hour)

16. Ментор распаковывает и проверяет
    ├─> Открывает project.zip
    ├─> Смотрит структуру
    ├─> Запускает приложение
    └─> Тестирует функциональность

17. Находит проблемы
    └─> Issues found:
        ├─ Missing requirements.txt
        ├─ Code не запускается (import error)
        └─> UI bug на главной странице

18. Status: "changes_requested"
    └─> Review Form:
        ├─ Score: 60 / 100
        ├─ Status: [changes_requested] ⚠️
        └─> Feedback:
            ├─ "❌ Проект не запускается"
            ├─ "Добавьте requirements.txt"
            ├─> "Исправьте import errors"

19. Submit review
    └─> Backend: POST /api/v1/submissions/reviews/
        └─> Submission.status = "changes_requested"
            └─> Студент получает notification

20. Студент исправляет и resubmit
    └─> POST /api/v1/submissions/{id}/revisions/
        └─> Создаёт новую SubmissionRevision
            └─> Submission снова появляется в mentor queue

21. Ментор review второй раз
    └─> Score: 95 / 100
        └─> Status: "approved" ✅
```

---



```
1-6. Как Сценарий 1

7. Выбрать coding assessment
   └─> /dashboard/mentor/assessments/{attempt_id}
       └─> Assessment Type: Coding
           ├─ Student: Jasur Rahimov
           ├─ Question: "Implement binary search"
           ├─ Programming Language: Python
           └─> Auto-check status: ⚠️ Partial pass

8. Просмотр auto-check results
   └─> Auto-check Results:
       ├─ Test Case 1: ✅ Pass (empty array)
       ├─ Test Case 2: ✅ Pass (single element)
       ├─ Test Case 3: ❌ Fail (large array)
       │   └─> Expected: 42, Got: -1
       ├─ Test Case 4: ✅ Pass (duplicates)
       └─> Auto Score: 75 / 100

9. Просмотр submitted code
   └─> Code Editor (read-only):
       ```python
       def binary_search(arr, target):
           left = 0
           right = len(arr) - 1
           
           while left <= right:
               mid = (left + right) // 2
               if arr[mid] == target:
                   return mid
               elif arr[mid] < target:
                   left = mid + 1
               else:
                   right = mid - 1
           
           return -1  
       ```

10. Ментор находит ошибку
    └─> Analysis:
        ├─> Логика правильная
        ├─> Но edge case не обработан
        └─> Test Case 3 failed из-за bug

11. Написать detailed feedback
    └─> Review Form:
        ├─ Override Auto Score: No (keep 75)
        │   (ИЛИ: Yes → Manual points: 80)
        └─> Feedback:
            ├─ "Алгоритм правильный! ✅"
            ├─> "Но Test Case 3 не прошёл из-за edge case"
            └─> "Подсказка: проверьте сортировку массива"

12. Submit review
    └─> Backend: POST /api/v1/assessment/reviews/{response_id}/
        ├─ mentor_points: null (keep auto_score)
        │   ИЛИ: 80 (override)
        └─ review_comment: "Алгоритм правильный..."
            └─> Final Score: 75 (auto) или 80 (manual)

13. Студент видит:
    ├─ Score: 75 / 100
    ├─ Status: ⚠️ Passed (но может улучшить)
    └─> Mentor feedback
```

---



```
1-3. Как Сценарий 1 (login, dashboard)

4. Offline Mentor Dashboard
   └─> Дополнительные секции:
       ├─ 👥 My Groups:
       │   ├─ Python Group 
       │   └─> Django Group 
       │
       ├─> 📅 Upcoming Sessions:
       │   ├─ Today 10:00 — Python Group 
       │   └─> Tomorrow 14:00 — Django Group 
       │
       └─> ⏰ Attendance needed:
           └─> Last session (not marked yet)

5. Нажать на Group
   └─> /dashboard/mentor/groups/{group_id}
       └─> Group Detail Page:
           ├─ Group: Python Group 
           ├─ Students: 15
           ├─ Schedule: Mon/Wed/Fri 10:00-12:00
           └─> Student List:
               ├─ Alisher Umarov (attendance: 90%)
               ├─ Shahzod Tursunov (attendance: 85%)
               └─> ... [15 students]

6. Начало занятия (сегодня 10:00)
   └─> Ментор приходит в класс
       └─> Открывает /dashboard/mentor/attendance

7. Отметить attendance
   └─> Attendance Page:
       ├─ Session: Python Group 
       ├─ Date: 2026-06-17
       ├─ Time: 10:00-12:00
       └─> Student checklist:
           ├─ [ ] Alisher Umarov
           ├─ [ ] Shahzod Tursunov
           └─> ... [15 students]

8. Отметить присутствующих
   └─> Для каждого студента:
       └─> [✓] Present / [ ] Absent / [ ] Late
           └─> Backend: POST /api/v1/mentorship/attendance/
               ├─ student_id
               ├─ session_id
               ├─ status: "present" / "absent" / "late"
               └─> Mentorship Domain:
                   └─> Создаёт/Обновляет Attendance

9. Submit attendance
   └─> Backend сохраняет
       └─> Событие: AttendanceMarked (Signal)
           └─> Progress Domain:
               └─> Для offline студентов:
                   └─> Отмечает lessons как completed
                       (если attendance + homework done)

10. После занятия: дать homework
    └─> Ментор создаёт Assignment для урока
        └─> Backend: POST /api/v1/submissions/assignments/
            ├─ lesson_id
            ├─ title: "Homework 
            ├─ description: "..."
            └─ deadline_offset_days: 7

11. Студенты видят новый assignment
    └─> В lesson page появляется homework
        └─> Студенты submit работы

12. Ментор review submissions
    └─> Как Сценарий 1 (steps 11-18)
```

---



```
1-12. Как Сценарий 1

13. Ментор в Submissions Queue
    └─> Видит 15 pending submissions
        └─> Похожие задания (Homework 

14. Открывает первую
    └─> Review + Submit
        └─> Автоматически открывает следующую

15. Quick Review Mode (опция)
    └─> UI оптимизирован для быстрого review:
        ├─ Навигация: [Previous] [Next]
        ├─> Score dropdown (preset values)
        ├─> Status radio buttons
        └─> Template feedback (common comments)

16. Review 15 submissions за 1 час
    └─> Каждая ~4 минуты:
        ├─ Открыть работу (30s)
        ├─ Проверить (2-3 min)
        └─> Submit review (30s)

17. Progress tracker
    └─> UI показывает:
        ├─ Reviewed: 15 / 15 ✅
        ├─> Time: 1 hour
        └─> Average: 4 min per submission
```

---



```
1-3. Как Сценарий 1

4. Студент приходит к ментору
   └─> "Я сдал проект, но система не засчитала"

5. Ментор проверяет
   └─> Login → Dashboard → Search student
       └─> Find: "Alisher Umarov"
           └─> View Progress

6. Просмотр student progress
   └─> /dashboard/mentor/students/{student_id}/progress
       └─> Course Progress:
           ├─ Module 1: ✅ Completed
           ├─ Module 2: ⏳ In Progress
           │   ├─ Lesson 1: ✅ Completed
           │   ├─ Lesson 2: ⏳ Stuck (99% но не completed)
           │   └─> Lesson 3: 🔒 Locked
           └─> Module 3: 🔒 Locked

7. Ментор видит проблему
   └─> Lesson 2: все контенты viewed, но status != completed
       └─> Может быть technical glitch

8. Ментор проверяет работу студента
   ├─> Студент демонстрирует знания
   └─> Решение: Manual override

9. Override lesson completion
   └─> Backend: POST /api/v1/mentorship/override/lesson-completion/
       ├─ student_id
       ├─ lesson_id
       ├─ override_reason: "Technical glitch, student demonstrated knowledge"
       └─> Mentorship Domain:
           └─> Progress Domain:
               ├─> LessonProgress.status = "completed"
               ├─> Audit: override_by = mentor_id
               └─> Событие: LessonCompletionOverride

10. Lesson 3 разблокирован
    └─> Студент может продолжить обучение
        └─> Audit trail сохранён (кто, когда, почему)
```

---



```
1-3. Как Сценарий 1

4. Ментор на Dashboard
   └─> Нажать "Statistics" tab
       └─> /dashboard/mentor/statistics

5. Statistics Page
   └─> Overview:
       ├─ 📊 This Week:
       │   ├─ Reviews completed: 47
       │   ├─ Average score: 82 / 100
       │   └─> Average review time: 5.2 min
       │
       ├─> 📈 This Month:
       │   ├─ Total reviews: 203
       │   ├─> Students helped: 35
       │   └─> Courses covered: 3
       │
       └─> 🎯 Performance:
           ├─ Response time: 3.5 hours (avg)
           ├─> Student satisfaction: 4.8 / 5.0
           └─> Re-submission rate: 12%

6. Export report
   └─> Button "Export CSV"
       └─> Downloads report.csv
           ├─ Date, Student, Assignment, Score
           └─> Для admin reporting

7. View student-specific stats
   └─> Search: "Alisher Umarov"
       └─> Student Report:
           ├─ Total submissions: 12
           ├─ Average score: 88 / 100
           ├─> Improvement trend: ↗️ +15%
           └─> Areas needing attention: [list]
```

---




- `GET /api/v1/assessment/reviews/pending/` — Pending assessments queue
- `GET /api/v1/assessment/attempts/{id}/` — Assessment detail for review
- `POST /api/v1/assessment/reviews/{response_id}/` — Submit review
- `GET /api/v1/assessment/reviews/my/` — My completed reviews


- `GET /api/v1/submissions/reviews/pending/` — Pending submissions queue
- `GET /api/v1/submissions/submissions/{id}/` — Submission detail
- `POST /api/v1/submissions/reviews/` — Submit review
- `GET /api/v1/submissions/uploads/download-url/{file_id}/` — Download file
- `GET /api/v1/submissions/reviews/my/` — My completed reviews


- `GET /api/v1/mentorship/groups/` — My mentor groups
- `GET /api/v1/mentorship/groups/{id}/` — Group detail
- `GET /api/v1/mentorship/sessions/upcoming/` — Upcoming sessions
- `POST /api/v1/mentorship/attendance/` — Mark attendance
- `GET /api/v1/mentorship/attendance/{session_id}/` — Session attendance
- `POST /api/v1/mentorship/override/lesson-completion/` — Override completion


- `GET /api/v1/mentorship/students/` — My students list
- `GET /api/v1/mentorship/students/{id}/progress/` — Student progress
- `GET /api/v1/mentorship/students/{id}/submissions/` — Student submissions
- `GET /api/v1/mentorship/students/{id}/assessments/` — Student assessments


- `GET /api/v1/mentorship/statistics/` — My statistics
- `GET /api/v1/mentorship/reports/weekly/` — Weekly report
- `GET /api/v1/mentorship/reports/monthly/` — Monthly report

---



| Action | Online Mentor | Offline Mentor | Staff | Admin |
|--------|---------------|----------------|-------|-------|
| **Assessment Reviews** |
| View pending assessments | ✅ ALL | ✅ Own students | ✅ ALL | ✅ ALL |
| Review quiz | ✅ | ✅ | ✅ | ✅ |
| Review essay | ✅ | ✅ | ✅ | ✅ |
| Review coding | ✅ | ✅ | ✅ | ✅ |
| Override auto-score | ✅ | ✅ | ✅ | ✅ |
| **Submission Reviews** |
| View pending submissions | ✅ ALL | ✅ Own students | ✅ ALL | ✅ ALL |
| Download files | ✅ | ✅ | ✅ | ✅ |
| Approve/Reject | ✅ | ✅ | ✅ | ✅ |
| Request changes | ✅ | ✅ | ✅ | ✅ |
| **Mentorship (Offline)** |
| View groups | — | ✅ Own | ✅ ALL | ✅ ALL |
| Mark attendance | — | ✅ Own | ✅ ALL | ✅ ALL |
| Create assignments | — | ✅ Own | ✅ ALL | ✅ ALL |
| Override completion | — | ✅ Own | ✅ ALL | ✅ ALL |
| **Reports** |
| View own stats | ✅ | ✅ | ✅ | ✅ |
| Export own reports | ✅ | ✅ | ✅ | ✅ |
| View all mentors stats | — | — | ✅ | ✅ |

---




```
09:00 — Login → Check dashboard
        └─> Pending count: Assessments (5) + Submissions (12)

09:15 — Start with urgent items (>24h waiting)
10:00 — Review coding assessments (need focus)
11:00 — Review submissions (can be faster)
12:00 — Break

14:00 — Continue submissions
15:00 — Mark attendance (if offline mentor)
16:00 — Create assignments for next week
17:00 — Check statistics, plan tomorrow
```


```
Priority 1 (URGENT):
- Waiting > 2 days
- Student blocked (can't progress)
- Final assessments

Priority 2 (HIGH):
- Waiting > 1 day
- Coding assessments (complex)

Priority 3 (NORMAL):
- Waiting < 1 day
- Simple homework reviews
```


```
✅ Approved:
"Отличная работа! Все требования выполнены."

⚠️ Changes Requested:
"Хорошее начало, но исправьте:
1. [issue 1]
2. [issue 2]
Resubmit после исправлений."

❌ Rejected:
"К сожалению, работа не соответствует требованиям.
Начните заново и обратите внимание на: [list]"
```

---




```
1. Ментор открывает submission
2. GitHub link: 404 Not Found
3. Status: "changes_requested"
4. Feedback: "Ссылка не работает, проверьте доступ к repo"
```


```
1. Студент пишет: "Почему только 70?"
2. Ментор может:
   ├─> Пересмотреть review (если ошибся)
   ├─> Объяснить оценку (в комментариях)
   └─> Эскалировать в Support (если conflict)
```


```
1. Coding assessment: auto_check_result = null
2. Ментор видит: "⚠️ Auto-check failed"
3. Must review manually (cannot rely on auto-score)
```


```
1. Student resubmit 3 раза
2. Mentor sees: Revision history (v1, v2, v3)
3. Can compare versions
4. Decision: Approve with lower score ИЛИ Escalate
```

---



1. ✅ Login & Dashboard
2. ✅ Assessment Reviews (quiz, essay, coding)
3. ✅ Submission Reviews (GitHub, file, text, link)
4. ✅ File Downloads (S3 presigned URLs)
5. ✅ Feedback & Scoring
6. ✅ Offline: Groups & Attendance
7. ✅ Offline: Assignment Creation
8. ✅ Override Lesson Completion
9. ✅ Statistics & Reports
10. ✅ Student Progress Tracking

**All Mentor flows работают!** 🎓
