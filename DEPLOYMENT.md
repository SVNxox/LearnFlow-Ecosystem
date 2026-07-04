



This guide covers deploying LearnFlow to production using Docker Compose with:
- **Nginx** (reverse proxy + static files + SSL)
- **Gunicorn** (WSGI server, 4 workers)
- **PostgreSQL 16** (database)
- **Redis 7** (cache + Celery broker)
- **Celery** (3 workers + beat scheduler)

---





```bash

- Ubuntu 22.04 LTS or later
- 4GB RAM minimum (8GB recommended)
- 20GB disk space
- Docker 24.x + Docker Compose v2
- Domain name with DNS configured
```



```bash

sudo apt update && sudo apt upgrade -y


curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh


sudo apt install docker-compose-plugin -y


sudo usermod -aG docker $USER
newgrp docker


docker --version
docker compose version
```



```bash

git clone https://github.com/yourorg/learnflow.git
cd learnflow


cp .env.production.example .env.production


nano .env.production
```



```bash

python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


ssh-keygen -t rsa -b 2048 -m PEM -f jwt-key -N ""
cat jwt-key | sed ':a;N;$!ba;s/\n/\\n/g'        
cat jwt-key.pub | sed ':a;N;$!ba;s/\n/\\n/g'    
rm jwt-key jwt-key.pub  


openssl rand -base64 32  
openssl rand -base64 32  
```



**Option A: Let's Encrypt (Recommended)**

```bash

sudo apt install certbot -y


sudo certbot certonly --standalone -d learnflow.uz -d www.learnflow.uz -d api.learnflow.uz


sudo cp /etc/letsencrypt/live/learnflow.uz/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/learnflow.uz/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*.pem


sudo crontab -e

```

**Option B: Self-signed (Development Only)**

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=learnflow.uz"
```



```bash

docker compose -f docker-compose.prod.yml up -d --build


docker compose -f docker-compose.prod.yml logs -f


docker compose -f docker-compose.prod.yml ps


docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---





```bash

curl https://learnflow.uz/api/v1/health/
```



```bash

docker compose -f docker-compose.prod.yml ps










```



```bash

docker compose -f docker-compose.prod.yml logs web


docker compose -f docker-compose.prod.yml logs worker-default


docker compose -f docker-compose.prod.yml logs db


docker compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/learnflow_access.log
```

---





```bash

git pull origin main


docker compose -f docker-compose.prod.yml up -d --build


docker compose -f docker-compose.prod.yml exec web python manage.py migrate


docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```



```bash

docker compose -f docker-compose.prod.yml exec db pg_dump -U learnflow learnflow > backup_$(date +%Y%m%d_%H%M%S).sql


docker compose -f docker-compose.prod.yml exec -T db psql -U learnflow learnflow < backup_20260704_023000.sql
```



```bash

docker compose -f docker-compose.prod.yml up -d --scale worker-default=4
```



```bash

docker compose -f docker-compose.prod.yml exec worker-default celery -A learnflow inspect active


docker compose -f docker-compose.prod.yml exec worker-default celery -A learnflow inspect registered
```



```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

---



- [ ] Strong `SECRET_KEY` generated (50+ chars)
- [ ] Strong `POSTGRES_PASSWORD` (20+ chars)
- [ ] Strong `REDIS_PASSWORD` (20+ chars)
- [ ] JWT RSA keys generated (2048-bit)
- [ ] `.env.production` is NOT committed to git (add to `.gitignore`)
- [ ] SSL certificates configured (Let's Encrypt recommended)
- [ ] `DEBUG=False` in `.env.production`
- [ ] `ALLOWED_HOSTS` configured with actual domain
- [ ] CORS origins restricted to your frontend domain
- [ ] Admin panel access restricted (consider IP whitelist in nginx config)
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Database backups automated
- [ ] Sentry configured for error tracking (optional)

---





```bash

docker stats


docker system df


du -sh logs/
```



- **Prometheus** + **Grafana** (metrics)
- **Sentry** (error tracking)
- **Uptime Robot** (uptime monitoring)
- **Cloudflare** (DDoS protection + CDN)

---





```bash

docker compose -f docker-compose.prod.yml logs <service-name>


docker compose -f docker-compose.prod.yml ps


docker compose -f docker-compose.prod.yml restart <service-name>
```



```bash

docker compose -f docker-compose.prod.yml exec db psql -U learnflow -d learnflow -c "SELECT version();"



```



```bash

docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput


docker compose -f docker-compose.prod.yml exec nginx ls -la /app/staticfiles/
```



```bash

docker compose -f docker-compose.prod.yml logs worker-default


docker compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping


docker compose -f docker-compose.prod.yml restart worker-default worker-email worker-notifications
```



```bash

docker stats --no-stream






```

---



```bash

git pull origin main


docker compose -f docker-compose.prod.yml build


docker compose -f docker-compose.prod.yml up -d --scale web=2 --no-recreate


docker compose -f docker-compose.prod.yml ps


docker compose -f docker-compose.prod.yml up -d --scale web=1


docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---



- **Documentation**: `docs/`
- **GitHub Issues**: https://github.com/yourorg/learnflow/issues
- **Email**: support@learnflow.uz

---



See `.env.production.example` for complete list of required and optional environment variables.

**Critical variables:**
- `SECRET_KEY` — Django secret key
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` — RSA keys for JWT
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — S3 credentials
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — SMTP credentials
- `TELEGRAM_BOT_TOKEN` — Telegram bot token

---

**Last Updated:** 2026-07-04
