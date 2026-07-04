



| Параметр | Значение |
|----------|----------|
| Base URL | `/api/v1/` |
| Auth | `Authorization: Bearer <JWT>` |
| Format | JSON |
| Pagination | `{ count, next, previous, results }` |
| Errors | `{ error, code, detail }` |
| IDs | UUID везде |
| Timestamps | ISO 8601 с таймзоной |

---



```
POST /api/auth/token/          
POST /api/auth/token/refresh/  
POST /api/auth/register/       
POST /api/auth/logout/         
```

---




```
GET  /api/v1/learning/courses/              
GET  /api/v1/learning/courses/{slug}/       
GET  /api/v1/learning/categories/           
```


```
POST   /api/v1/learning/courses/                    
PATCH  /api/v1/learning/courses/{id}/               
POST   /api/v1/learning/courses/{id}/publish/       
POST   /api/v1/learning/courses/{id}/archive/       

POST   /api/v1/learning/courses/{id}/modules/       
PATCH  /api/v1/learning/modules/{id}/               
POST   /api/v1/learning/courses/{id}/modules/reorder/  

POST   /api/v1/learning/modules/{id}/lessons/       
PATCH  /api/v1/learning/lessons/{id}/               
POST   /api/v1/learning/modules/{id}/lessons/reorder/  

POST   /api/v1/learning/lessons/{id}/content/       
PATCH  /api/v1/learning/content/{id}/               
DELETE /api/v1/learning/content/{id}/               
POST   /api/v1/learning/lessons/{id}/content/reorder/

POST   /api/v1/learning/lessons/{id}/homework/      
DELETE /api/v1/learning/lessons/{id}/homework/      

POST   /api/v1/learning/lessons/{id}/quiz/          
POST   /api/v1/learning/quizzes/{id}/questions/     
```


```
GET  /api/v1/learning/modules/{id}/lessons/{id}/    
```


```
POST /api/v1/learning/enrollments/                  
GET  /api/v1/learning/enrollments/me/               
POST /api/v1/learning/enrollments/{id}/drop/        
GET  /api/v1/learning/courses/{id}/enrollments/     
```

---



```
GET  /api/v1/progress/me/                           
GET  /api/v1/progress/courses/{course_id}/          
GET  /api/v1/progress/courses/{course_id}/next/     
GET  /api/v1/progress/lessons/{lesson_id}/          

POST /api/v1/progress/lessons/{id}/content/{id}/view/  
                                                        
                                                        

POST /api/v1/progress/enrollments/{id}/lessons/{id}/complete/  
GET  /api/v1/progress/courses/{id}/students/        
GET  /api/v1/progress/students/{id}/courses/{id}/   
```



```json
{
  "type": "lesson",
  "lesson_id": "uuid",
  "lesson_title": "Введение в Django ORM",
  "module_title": "Модуль 2: База данных"
}
```

```json
{
  "type": "take_module_assessment",
  "module_id": "uuid",
  "module_title": "Модуль 1: Python основы",
  "assessment_title": "Итоговый тест"
}
```

```json
{ "type": "course_complete" }
```

---




```
GET  /api/v1/assessments/modules/{module_id}/           
POST /api/v1/assessments/modules/{module_id}/attempts/  
GET  /api/v1/assessments/attempts/{id}/                 
PATCH /api/v1/assessments/attempts/{id}/responses/{item_id}/  
POST /api/v1/assessments/attempts/{id}/submit/          
GET  /api/v1/assessments/attempts/{id}/result/          
```


```
GET  /api/v1/assessments/pending-review/                
GET  /api/v1/assessments/attempts/{id}/grade/           
POST /api/v1/assessments/attempts/{id}/responses/{item_id}/grade/  
POST /api/v1/assessments/attempts/{id}/complete-grading/            
```


```
POST  /api/v1/assessments/modules/{id}/                 
PATCH /api/v1/assessments/{id}/                         
POST  /api/v1/assessments/{id}/items/                   
POST  /api/v1/assessments/items/{id}/options/           
POST  /api/v1/assessments/items/{id}/test-cases/        
POST  /api/v1/assessments/{id}/publish/                 
```

---




```
GET  /api/v1/submissions/assignments/{id}/           
GET  /api/v1/submissions/my/                         
POST /api/v1/submissions/assignments/{id}/submit/    
GET  /api/v1/submissions/{id}/                       
POST /api/v1/submissions/{id}/revisions/             
GET  /api/v1/submissions/{id}/revisions/             
POST /api/v1/submissions/{id}/files/                 
GET  /api/v1/submissions/{id}/autochecks/            
```


```
GET  /api/v1/submissions/pending-review/             
GET  /api/v1/submissions/{id}/review/                
POST /api/v1/submissions/{id}/review/                
     Body: { score, feedback, status }
```


```
POST /api/v1/submissions/assignments/                
PATCH /api/v1/submissions/assignments/{id}/          
DELETE /api/v1/submissions/assignments/{id}/         
```

---




```
GET  /api/v1/mentorship/groups/my/                   
GET  /api/v1/mentorship/groups/{id}/                 
GET  /api/v1/mentorship/groups/{id}/students/        
POST /api/v1/mentorship/sessions/                    
GET  /api/v1/mentorship/sessions/{id}/               
POST /api/v1/mentorship/sessions/{id}/start/         
POST /api/v1/mentorship/sessions/{id}/attendance/    
     Body: { attendances: [{ student_id, status, notes }] }
POST /api/v1/mentorship/sessions/{id}/complete/      
GET  /api/v1/mentorship/work-queue/                  
```


```
POST /api/v1/mentorship/groups/                      
PATCH /api/v1/mentorship/groups/{id}/                
POST /api/v1/mentorship/groups/{id}/students/        
DELETE /api/v1/mentorship/groups/{id}/students/{id}/ 
```


```
GET  /api/v1/mentorship/access-events/               
GET  /api/v1/mentorship/groups/{id}/attendance-stats/ 
```

---




```
GET  /api/v1/certificates/my/                        
GET  /api/v1/certificates/{id}/                      
GET  /api/v1/certificates/{id}/download/             
POST /api/v1/certificates/{id}/reissue-request/      
     Body: { reason }
```


```
GET  /api/v1/certificates/verify/{verification_code}/ 
     Response: { valid, student_name, course_name, issue_date, status }
```


```
GET  /api/v1/certificates/                           
POST /api/v1/certificates/{id}/revoke/               
     Body: { reason }
POST /api/v1/certificates/templates/                 
PATCH /api/v1/certificates/templates/{id}/           
GET  /api/v1/certificates/reissue-requests/          
POST /api/v1/certificates/reissue-requests/{id}/approve/ 
POST /api/v1/certificates/reissue-requests/{id}/reject/  
```

---



| Code | HTTP | Описание |
|------|------|----------|
| `not_enrolled` | 403 | Студент не записан на курс |
| `lesson_locked` | 403 | Урок заблокирован |
| `course_not_published` | 400 | Курс ещё не опубликован |
| `duplicate_enrollment` | 409 | Уже записан на этот курс |
| `max_attempts_reached` | 400 | Превышено число попыток (assessment) |
| `attempt_expired` | 400 | Время истекло (assessment) |
| `publish_not_ready` | 400 | Курс не готов к публикации |
| `quiz_exists` | 409 | Уже есть quiz для этого урока |
| `has_active_enrollments` | 400 | Нельзя выполнить действие |
| `file_too_large` | 413 | Файл превышает максимальный размер |
| `file_scan_failed` | 400 | Файл не прошёл проверку на вирусы |
| `invalid_mime_type` | 400 | Недопустимый тип файла |
| `submission_not_found` | 404 | Submission не найден |
| `assignment_not_found` | 404 | Задание не найдено |
| `already_reviewed` | 409 | Submission уже проверен |
| `not_mentor_of_student` | 403 | Вы не ментор этого студента |
| `group_full` | 400 | Группа заполнена (max_students достигнут) |
| `session_not_started` | 400 | Занятие ещё не началось |
| `session_already_completed` | 400 | Занятие уже завершено |
| `attendance_already_marked` | 409 | Посещаемость уже отмечена |
| `certificate_not_issued` | 400 | Сертификат ещё не выдан |
| `certificate_revoked` | 400 | Сертификат отозван |
| `verification_code_invalid` | 404 | Неверный код верификации |
| `reissue_already_pending` | 409 | Запрос на переиздание уже существует |
