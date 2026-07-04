

Ushbu hujjat `LearnFlow_Himoya.pptx` taqdimotiga qo'shimcha material sifatida tayyorlangan: vaqt taqsimoti, dizayn asoslari va himoya paytida berilishi mumkin bo'lgan savollarga tayyor javoblar.

---



| 
|---|-------|-------|------|------|
| 1 | Title | Kirish, o'zini tanishtirish | 0:30 | 0:30 |
| 2 | Muammo | An'anaviy LMS'larning kamchiliklari | 0:45 | 1:15 |
| 3 | Yechim (ADR-002) | Bitta kurs — ikki format | 1:00 | 2:15 |
| 4 | Loyiha ko'lami | Raqamlar orqali jiddiylikni ko'rsatish | 0:30 | 2:45 |
| 5 | Arxitektura evolyutsiyasi | Monolit → Mikroservis strategiyasi | 1:00 | 3:45 |
| 6 | Migratsiyaga tayyorgarlik | Texnik detallar (qisqa) | 0:30 | 4:15 |
| 7 | Texnologik stek | Nega aynan shu texnologiyalar | 0:30 | 4:45 |
| 8 | DDD / qatlamlar | 4 qatlamli arxitektura | 0:45 | 5:30 |
| 9 | Event-Driven Architecture | Signals vs Outbox | 0:45 | 6:15 |
| 10 | Transactional Outbox | Chuqur texnik tushuntirish | 1:00 | 7:15 |
| 11 | Concurrency Control | Race condition demo | 0:45 | 8:00 |
| 12 | S3 Upload | Performance yechim | 0:30 | 8:30 |
| 13 | Xavfsizlik | Qisqa umumiy ko'rinish | 0:30 | 9:00 |
| 14 | Metrikalar | Real natijalar | 0:30 | 9:30 |
| 15 | Xulosa | Yakuniy taassurot | 0:30 | 10:00 |

**Maslahat:** Agar vaqt yetishmasa, birinchi bo'lib 6- va 13-slaydlarni qisqartiring — ular tayanch (backup) ma'lumot bo'lib, savol-javob paytida qaytib kelish mumkin.

---



- **Uslub:** Qorong'i (dark), premium texnologik keynote — Vercel, Linear va Stripe taqdimotlaridan ilhomlangan.
- **Palitra:** Chuqur navy-qora fon (`
- **Motiv:** Yumaloq ikonka-chip'lar (icon-in-circle) — har bir slaydda takrorlanadi, izchillikni ta'minlaydi.
- **Tipografika:** Calibri (sarlavhalar bold 28-72pt, matn 11-16pt) — PowerPoint'da barqaror ko'rinish uchun.
- **Har bir slayd** — bitta asosiy g'oya, minimal matn, vizual element (karta, diagramma, ikon, statistik ko'rsatkich).
- **Animatsiya tavsiyasi:** PowerPoint'da slaydlarni ochishda "Fade" o'tishini, kartalarni "Appear" bilan ketma-ket chiqarishni tavsiya qilaman (Transitions → Fade, Animations → Appear, "By paragraph" tartibida). Bu murakkab diagramma slaydlarida (9, 10, 11) tinglovchi diqqatini bosqichma-bosqich yo'naltiradi.

---




DevOps jamoasi yo'qligi, domen chegaralari hali shakllanmaganligi va tezroq rivojlanish imkoniyati sabab bo'ldi (ADR-001). Lekin kod darajasida mikroservisga tayyorgarlik ko'rilgan: UUID soft-reference, alohida Python package'lar, event-driven aloqa. Migratsiya taxminan 4 haftada amalga oshirilishi mumkin.


Uch darajali himoya: (1) `select_for_update()` — PostgreSQL row-level lock, (2) `F()` ifodalari — atomik DB darajasidagi increment, (3) idempotent handler'lar — bir xil eventni bir necha marta ishlashda xavfsiz.


RabbitMQ monolit uchun ortiqcha infratuzilma murakkabligini keltiradi va alohida failure-point yaratadi. Outbox Pattern esa qo'shimcha infratuzilmasiz kafolatlangan yetkazib berishni, audit trail'ni va SQL orqali oddiy monitoringni beradi. Kelajakda RabbitMQ'ga oson almashtiriladi.


Django — stateless, gorizontal masshtablanadi (Gunicorn workerlar + load balancer). PostgreSQL'da read replica va connection pooling (PgBouncer). Celery'da bir nechta worker pool va priority queue. S3 avtomatik masshtablanadi.


Hozircha test coverage 0% — bu ochiq texnik qarz sifatida hujjatlashtirilgan. Keyingi bosqichda pytest va pytest-django orqali 80% coverage maqsad qilingan. Bu — loyihaning kuchli va zaif tomonlarini halol baholash qobiliyatini ko'rsatadi.


JWT (access+refresh, rotatsiya), RBAC va row-level ruxsatlar, DRF serializer validatsiyasi, ORM orqali SQL Injection himoyasi, avtomatik XSS escaping, presigned URL'lar uchun content-type va hajm cheklovi, audit trail va soft-delete.


Django yetuk ekotizimga (18+ yil), tayyor ORM'ga, admin panelga va o'rnatilgan xavfsizlik mexanizmlariga ega. FastAPI'da bularning barchasini qo'lda yig'ish kerak bo'lardi — bu vaqt talab qiladi va loyihaning MVP muddatlariga mos kelmasdi.


`CourseEnrollment` modelida `delivery_format` maydoni (`online`/`offline`) mavjud. Content bitta manbada saqlanadi, faqat progress va topshiriqlarni topshirish jarayoni formatga qarab farqlanadi. Talaba hatto formatni almashtirishi ham mumkin.


Test coverage yo'qligi va to'liq monitoring (Prometheus/Grafana) hali joriy etilmaganligi — bu ochiq texnik qarz sifatida 26- va 27-bo'limlarda hujjatlashtirilgan. Bular Phase 2'ning asosiy ustuvorliklari.


Bu — eventual consistency va DB yukini muvozanatlashtirish natijasi. Kritik bo'lmagan holatlarda 10 soniya foydalanuvchi tajribasiga sezilarli ta'sir qilmaydi; agar kerak bo'lsa, bu qiymatni 5 soniyagacha kamaytirish mumkin.

---



Agar komissiya kodni jonli ko'rishni so'rasa, quyidagi fayllarni ko'rsatish tavsiya etiladi (hujjatning 25-bo'limiga muvofiq):
- `src/backend/submissions/domain/services/submission_service.py` — concurrency control namunasi
- `src/backend/shared/infrastructure/outbox/tasks.py` — Outbox processor
- `src/backend/shared/infrastructure/storage/s3_client.py` — Presigned URL generatsiyasi

---



Himoya davomida eng ko'p e'tibor qaratiladigan uchta slayd — **Transactional Outbox (10-slayd)**, **Concurrency Control (11-slayd)** va **Event-Driven Architecture (9-slayd)**. Bularni alohida mashq qilib chiqing, chunki komissiya odatda aynan shu texnik chuqurlikdagi savollarni beradi.

Omad tilaymiz! 🎓
