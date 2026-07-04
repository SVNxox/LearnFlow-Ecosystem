

**Последнее обновление:** 2026-06-08  
**Цель:** Единая точка входа для разработчиков и AI

---





1. **QUICK_START.md** — установка, запуск проекта, первые шаги
2. **README.md** — что такое LearnFlow, технологии
3. **CLAUDE.md** — карта проекта, архитектурные паттерны, инварианты
4. **docs/DOMAIN.md** — бизнес-логика, учебный флоу, роли
5. **docs/ARCHITECTURE.md** — модульный монолит, границы доменов
6. **docs/DATABASE.md** — схема БД (52 таблицы)
7. **docs/TESTING.md** — стратегия тестирования



**Обязательное чтение каждой сессии:**
1. `CLAUDE.md` → `docs/DOMAIN.md` → `docs/ARCHITECTURE.md` → `docs/DATABASE.md`

**Перед реализацией:** Прочитай дизайн-документ домена (`docs/design/`) + соответствующие ADR (`docs/DECISIONS.md`)

---



| Задача | Документы для чтения |
|--------|---------------------|
| **Установка и запуск** | QUICK_START.md → DEPLOYMENT.md (для production) |
| **Написание тестов** | TESTING.md → CONTRIBUTING.md (паттерны) |
| **Изменение структуры БД** | DATABASE.md → дизайн-документ домена → DECISIONS.md (соотв. ADR) |
| **Разработка API** | API.md → дизайн-документ домена → ARCHITECTURE.md (cross-domain) |
| **Безопасность** | SECURITY.md → ARCHITECTURE.md (event flow) |
| **Новый домен** | CONTRIBUTING.md → ARCHITECTURE.md → DATABASE.md → DECISIONS.md |
| **Архитектурное решение** | DECISIONS.md (читай ADR-001..029) → ARCHITECTURE.md |
| **Деплой/инфраструктура** | DEPLOYMENT.md → SECURITY.md |
| **Планирование микросервисов** | MICROSERVICES_ROADMAP.md → ARCHITECTURE.md (Event System) |
| **Текущие задачи** | TASKS.md (детальный статус каждого домена) |
| **История решений** | CONVERSATION_LOG.md → DECISIONS.md |

---





**Identity (accounts/)** — 100% готов
- Код: ✅ Models, selectors, services, events, API
- Статус: НЕ ТРОГАТЬ — домен закрыт



**Learning (courses/)** — 40% готов
- Код: ✅ Models (894 строк)
- Нужно: ❌ managers.py (БЛОКЕР), selectors, services, events, API
- Дизайн: docs/design/learnflow-learning-domain-v2.md



**UserProgress (progress/)** — дизайн готов
- Код: ❌ Домен не создан (папка не существует)
- Дизайн: docs/design/learnflow-userprogress-review-v2.md

**Assessment (assessment/)** — дизайн готов v3
- Код: ❌ Models пустые (60 байт)
- Дизайн: docs/design/ASSESSMENT_DOMAIN_V3.md
- Ключевые решения: ADR-010..013

**Submissions (submissions/)** — дизайн готов v1
- Код: ❌ Models пустые
- Дизайн: docs/design/SUBMISSIONS_DOMAIN_V1.md
- Ключевые решения: ADR-014..018

**Mentorship (mentorship/)** — дизайн готов v1
- Код: ❌ Домен не создан
- Дизайн: docs/design/MENTORSHIP_DOMAIN_V1.md
- Ключевые решения: ADR-019..023

**Certificates (certificates/)** — дизайн готов v1
- Код: ❌ Домен не создан
- Дизайн: docs/design/CERTIFICATES_DOMAIN_V1.md
- Ключевые решения: ADR-024..028



- Notifications (notifications/)
- Analytics (analytics/)

---




1. Прочти `CLAUDE.md` (инварианты, паттерны)
2. Прочти `docs/DOMAIN.md` (раздел домена)
3. Прочти `docs/design/{DOMAIN}_V{N}.md` (полный дизайн)
4. Прочти `docs/DATABASE.md` (таблицы домена)
5. Прочти `docs/API.md` (endpoints домена)
6. Прочти `docs/DECISIONS.md` (соответствующие ADR)


1. `models.py` → migrations
2. `selectors.py` (READ)
3. `services.py` (WRITE)
4. `events.py` + `handlers.py`
5. `tasks.py` (Celery)
6. `api/` (views, serializers, urls)
7. `tests/`


- ✅ Selector не мутирует данные
- ✅ Service использует `transaction.atomic()`
- ✅ События через `transaction.on_commit()`
- ✅ Счётчики через `F()` expressions
- ✅ Fan-out → Celery task
- ✅ `select_for_update()` в completion cascade

---




- [CLAUDE.md](../CLAUDE.md) — карта проекта для AI
- [TASKS.md](../TASKS.md) — текущие задачи и статус
- [README.md](../README.md) — описание проекта


- [QUICK_START.md](QUICK_START.md) — быстрый старт для новых разработчиков
- [DOMAIN.md](DOMAIN.md) — бизнес-логика
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [DATABASE.md](DATABASE.md) — схема БД
- [API.md](API.md) — REST API endpoints
- [SECURITY.md](SECURITY.md) — безопасность
- [TESTING.md](TESTING.md) — стратегия тестирования
- [DECISIONS.md](DECISIONS.md) — архитектурные решения (ADR)
- [ROADMAP.md](ROADMAP.md) — дорожная карта
- [MICROSERVICES_ROADMAP.md](MICROSERVICES_ROADMAP.md) — план экстракции в микросервисы
- [CONTRIBUTING.md](CONTRIBUTING.md) — гайд для контрибьюторов
- [DEPLOYMENT.md](DEPLOYMENT.md) — деплой и инфраструктура
- [CONVERSATION_LOG.md](CONVERSATION_LOG.md) — история обсуждений


- [Learning Domain v2](design/learnflow-learning-domain-v2.md)
- [Learning Application Layer](design/learnflow-application-layer.md)
- [UserProgress Domain v2](design/learnflow-userprogress-review-v2.md)
- [Assessment Domain v3](design/ASSESSMENT_DOMAIN_V3.md)
- [Submissions Domain v1](design/SUBMISSIONS_DOMAIN_V1.md)
- [Mentorship Domain v1](design/MENTORSHIP_DOMAIN_V1.md)
- [Certificates Domain v1](design/CERTIFICATES_DOMAIN_V1.md)

---



**Phase 1A:** ✅ Завершён (2026-06-07/08)
- Дизайн Assessment v3, Submissions v1, Mentorship v1, Certificates v1
- 35+ таблиц спроектированы
- 19 новых ADR (ADR-010..028)

**Phase 1B:** 🔴 Текущий (реализация кода)
1. Починить Learning Domain (`courses/managers.py` → БЛОКЕР)
2. Завершить Learning Domain (selectors, services, events, API)
3. Создать UserProgress Domain с нуля
4. Реализовать Assessment Domain v3
5. Реализовать Submissions Domain v1
6. Реализовать Mentorship Domain v1

**Phase 2:** ⏳ Планируется
- Integration tests
- Certificates Domain (PDF generation)
- Базовый Admin UI

---




- Перед кодом читай дизайн-документ — там все детали
- Если документация противоречива — останови код, спроси уточнение
- Если нашёл баг в дизайне — обнови CONVERSATION_LOG.md
- Если принял архитектурное решение — создай ADR в DECISIONS.md


- Не предполагай структуру БД — всегда проверяй DATABASE.md
- Не придумывай поля/события — только то что в документации
- Перед реализацией опиши: что читал, какие домены, как понял задачу
- Если документация устарела — останови работу, сообщи об этом

---



**Q: Где найти схему БД?**  
A: `docs/DATABASE.md` — полная схема всех 52 таблиц

**Q: Как взаимодействуют домены?**  
A: `docs/ARCHITECTURE.md` раздел "Cross-domain взаимодействие" + `CLAUDE.md` раздел 6

**Q: Где описаны бизнес-правила?**  
A: `docs/DOMAIN.md` раздел "Ключевые бизнес-правила" (BR-01..10)

**Q: Почему нет Course.mode поля?**  
A: ADR-002 в DECISIONS.md — режим живёт в `CourseEnrollment.delivery_format`

**Q: Как проверить файл на вирусы?**  
A: ADR-018 в DECISIONS.md — ClamAV scan через Celery

**Q: Можно ли откатить completion урока?**  
A: Нет — инвариант 

**Q: Почему Assessment без type поля?**  
A: ADR-010 в DECISIONS.md — Assessment = контейнер, состав определяется через items

**Q: Как ментор отмечает attendance?**  
A: ADR-021 в DECISIONS.md — вручную, турникет = подсказка

---



**Вопросы по документации:** Создай issue в репозитории  
**Предложения по улучшению:** Pull request в docs/

**Помни:** Документация — источник истины. Код должен соответствовать документации, а не наоборот.
