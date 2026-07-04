



- [ ] Read `DEPLOYMENT.md` completely
- [ ] Server meets requirements (4GB RAM, 20GB disk, Ubuntu 22.04+)
- [ ] Docker & Docker Compose installed
- [ ] Domain DNS configured (A records for learnflow.uz, www, api)
- [ ] SSL certificates obtained (Let's Encrypt recommended)



- [ ] `.env.production` created from `.env.production.example`
- [ ] `SECRET_KEY` generated (50+ random chars)
- [ ] `POSTGRES_PASSWORD` set (20+ random chars)
- [ ] `REDIS_PASSWORD` set (20+ random chars)
- [ ] JWT keys generated (RSA 2048-bit)
- [ ] `DATABASE_URL` configured
- [ ] `ALLOWED_HOSTS` set to actual domains
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend URL
- [ ] Email SMTP credentials configured
- [ ] S3/R2 storage credentials configured
- [ ] Telegram bot token configured
- [ ] Payment gateway token configured
- [ ] `DEBUG=False` verified



- [ ] `.env.production` added to `.gitignore`
- [ ] SSL certificates in `nginx/ssl/`
- [ ] Firewall rules configured (ports 80, 443, 22 only)
- [ ] SSH key-based auth enabled (password auth disabled)
- [ ] Non-root user created for deployment
- [ ] Admin panel IP whitelist considered
- [ ] Database backups automated
- [ ] Secrets stored in password manager
- [ ] No secrets in git history



- [ ] `docker compose -f docker-compose.prod.yml build`
- [ ] `docker compose -f docker-compose.prod.yml up -d`
- [ ] All services showing "healthy" in `docker compose ps`
- [ ] Health check returns 200: `curl https://learnflow.uz/api/v1/health/`
- [ ] Superuser created
- [ ] Admin panel accessible at `/admin/`
- [ ] API docs accessible at `/api/schema/swagger-ui/`
- [ ] Static files loading correctly
- [ ] Test user registration flow
- [ ] Test email sending
- [ ] Test file upload
- [ ] Test Celery tasks processing



- [ ] Error logs reviewed: `docker compose -f docker-compose.prod.yml logs`
- [ ] Sentry configured (optional but recommended)
- [ ] Uptime monitoring configured
- [ ] SSL certificate expiry alerts configured
- [ ] Disk space monitoring configured
- [ ] Database backup verification



- [ ] Server access documented (who has SSH access)
- [ ] Secrets location documented (password manager)
- [ ] Backup/restore procedure tested
- [ ] Rollback procedure documented
- [ ] On-call rotation defined (if team)



- [ ] Announced to team
- [ ] Monitoring dashboard reviewed
- [ ] First 24h: check logs hourly
- [ ] Performance metrics baselined
- [ ] Load testing conducted (optional)

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Production URL:** https://learnflow.uz
**Admin Panel:** https://learnflow.uz/admin/

**Notes:**


