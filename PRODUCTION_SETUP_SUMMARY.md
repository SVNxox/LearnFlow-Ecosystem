

**Created:** 2026-07-04  
**Status:** Ready for deployment

---





| File | Purpose |
|------|---------|
| `Dockerfile.prod` | Multi-stage production Dockerfile with non-root user |
| `docker-compose.prod.yml` | Production orchestration (8 services) |
| `entrypoint.sh` | Startup script (migrations, collectstatic, healthcheck) |



| File | Purpose |
|------|---------|
| `nginx/nginx.conf` | Main nginx config with gzip, rate limiting |
| `nginx/conf.d/learnflow.conf` | Site config with SSL, security headers |
| `nginx/ssl/` | Directory for SSL certificates (empty, add your certs) |



| File | Purpose |
|------|---------|
| `.env.production.example` | Template with all required variables |
| `.gitignore.production` | Production-specific gitignore rules |



| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | Complete deployment guide (SSL, secrets, operations) |
| `PRODUCTION_CHECKLIST.md` | Step-by-step deployment checklist |
| `PRODUCTION_SETUP_SUMMARY.md` | This file |



| File | Changes |
|------|---------|
| `requirements.txt` | Added: gunicorn, whitenoise, sentry-sdk |
| `learnflow/settings/production.py` | Added: WhiteNoise, Sentry, connection pooling, structured logging |
| `learnflow/urls.py` | Added: `/api/v1/health/` endpoint |

---



```
Internet
    ↓
Nginx (Port 80/443)
    ↓ reverse proxy
Gunicorn (4 workers, 2 threads)
    ↓
Django Application
    ↓
PostgreSQL 16 + Redis 7
    ↓
Celery (3 workers + beat)
```



1. **db** — PostgreSQL 16 (data persistence)
2. **redis** — Redis 7 (cache + Celery broker)
3. **web** — Django + Gunicorn (4 workers)
4. **worker-default** — Celery worker (general tasks)
5. **worker-email** — Celery worker (email queue)
6. **worker-notifications** — Celery worker (notifications)
7. **beat** — Celery Beat (scheduled tasks)
8. **nginx** — Reverse proxy + static files + SSL

---



- [x] HTTPS redirect (80 → 443)
- [x] HSTS (1 year, includeSubdomains, preload)
- [x] Security headers (X-Frame-Options, CSP, etc.)
- [x] Rate limiting (5 req/min auth, 10 req/s API)
- [x] Non-root container user
- [x] Secret management via .env.production
- [x] SSL/TLS 1.2+ only
- [x] Session cookies secure
- [x] CSRF cookies secure
- [x] Static files with far-future cache headers (WhiteNoise)
- [x] PostgreSQL statement timeout (30s)
- [x] Gunicorn graceful shutdown (30s)
- [x] Health checks on all services

---




- Workers: 4 (adjust based on CPU: 2-4 × CPU cores)
- Threads: 2 per worker
- Timeout: 60s
- Graceful timeout: 30s
- Max requests: 1000 (with jitter 50)


- Default worker: 4 concurrency, 300s timeout
- Email worker: 2 concurrency, 120s timeout
- Notifications worker: 2 concurrency, 120s timeout
- Max tasks per child: 100 (prevents memory leaks)


- Connection pool: 600s (CONN_MAX_AGE)
- Statement timeout: 30s
- Healthcheck: every 10s


- Max memory: 512MB
- Eviction policy: allkeys-lru
- Password protected

---



```bash

cp .env.production.example .env.production












nano .env.production  


docker compose -f docker-compose.prod.yml up -d --build


docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser


curl https://learnflow.uz/api/v1/health/

```

---



1. **Generate ALL secrets** (see DEPLOYMENT.md § 4)
   - SECRET_KEY (Django)
   - POSTGRES_PASSWORD (strong password)
   - REDIS_PASSWORD (strong password)
   - JWT_PRIVATE_KEY + JWT_PUBLIC_KEY (RSA 2048-bit)

2. **Obtain SSL certificates** (Let's Encrypt recommended)
   - Place in `nginx/ssl/fullchain.pem` and `nginx/ssl/privkey.pem`

3. **Configure S3/R2 storage**
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_STORAGE_BUCKET_NAME
   - AWS_S3_ENDPOINT_URL (for Cloudflare R2)

4. **Configure email SMTP**
   - EMAIL_HOST_USER
   - EMAIL_HOST_PASSWORD

5. **Configure payment gateway**
   - CLICK_PROVIDER_TOKEN (Click.uz)

6. **Configure Telegram bot**
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_BOT_USERNAME

7. **Review and edit**
   - `nginx/conf.d/learnflow.conf` — Update server_name with your domains
   - `.env.production` — Update ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS

---




- [ ] Check logs hourly: `docker compose -f docker-compose.prod.yml logs -f`
- [ ] Monitor health: `curl https://learnflow.uz/api/v1/health/`
- [ ] Test user registration
- [ ] Test email sending
- [ ] Test file upload
- [ ] Test Celery tasks


- [ ] Setup Sentry for error tracking
- [ ] Setup uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure database backups (daily cron)
- [ ] Setup SSL certificate auto-renewal
- [ ] Monitor disk usage
- [ ] Monitor memory usage
- [ ] Review logs weekly

---




```bash
docker compose -f docker-compose.prod.yml logs <service-name>
docker compose -f docker-compose.prod.yml restart <service-name>
```


```bash

docker compose -f docker-compose.prod.yml exec db psql -U learnflow -d learnflow -c "SELECT version();"
```


```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml restart nginx
```


```bash
docker compose -f docker-compose.prod.yml logs worker-default
docker compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping
```

---



- **Full Guide:** `DEPLOYMENT.md`
- **Checklist:** `PRODUCTION_CHECKLIST.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Issues:** GitHub Issues

---



| Category | Status | Notes |
|----------|--------|-------|
| Docker config | ✅ Ready | Multi-stage, non-root, healthchecks |
| Nginx config | ✅ Ready | SSL, security headers, rate limiting |
| Django settings | ✅ Ready | Production hardening, WhiteNoise, Sentry |
| Secrets template | ✅ Ready | All required vars documented |
| Healthcheck endpoint | ✅ Ready | `/api/v1/health/` |
| Static files | ✅ Ready | WhiteNoise + Nginx |
| Celery workers | ✅ Ready | 3 queues + beat scheduler |
| Documentation | ✅ Ready | Deployment guide + checklist |

---

**Next Step:** Follow `DEPLOYMENT.md` to deploy to production server.

**Estimated Deployment Time:** 30-60 minutes (first time)

---

*Generated: 2026-07-04T02:35:58Z*
