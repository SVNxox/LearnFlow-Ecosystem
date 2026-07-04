# SSL Setup для learnflow.cloud-ip.cc

## Шаг 1: Установка Certbot

```bash
sudo apt update
sudo apt install certbot -y
```

## Шаг 2: Остановка nginx (если запущен)

```bash
sudo systemctl stop nginx
# или если через Docker:
docker-compose down
```

## Шаг 3: Получение SSL сертификата

```bash
sudo certbot certonly --standalone \
  -d learnflow.cloud-ip.cc \
  -d www.learnflow.cloud-ip.cc \
  -d api.learnflow.cloud-ip.cc
```

**Важно:** Убедись, что:
- Порты 80 и 443 открыты в firewall
- DNS записи A указывают на IP сервера:
  - `learnflow.cloud-ip.cc` → твой IP
  - `www.learnflow.cloud-ip.cc` → твой IP
  - `api.learnflow.cloud-ip.cc` → твой IP

## Шаг 4: Создание директории для SSL

```bash
mkdir -p nginx/ssl
```

## Шаг 5: Копирование сертификатов

```bash
sudo cp /etc/letsencrypt/live/learnflow.cloud-ip.cc/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/learnflow.cloud-ip.cc/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

## Шаг 6: Настройка автопродления

Добавь в crontab:

```bash
sudo crontab -e
```

Добавь строку (проверка каждый день в 3:00):

```cron
0 3 * * * certbot renew --quiet --post-hook "docker-compose -f /home/ubuntu/learnflow/LearnFlow-Ecosystem/docker-compose.prod.yml restart nginx"
```

**Если без Docker:**

```cron
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

## Шаг 7: Проверка конфигурации nginx

```bash
# Если через Docker:
docker-compose -f docker-compose.prod.yml config

# Если напрямую:
sudo nginx -t
```

## Шаг 8: Запуск

```bash
# Через Docker (production):
docker-compose -f docker-compose.prod.yml up -d

# Или через systemd:
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Проверка SSL

Открой в браузере:
- https://learnflow.cloud-ip.cc
- https://api.learnflow.cloud-ip.cc/api/v1/health/

Или через curl:

```bash
curl -I https://learnflow.cloud-ip.cc
curl https://api.learnflow.cloud-ip.cc/api/v1/health/
```

## Тест SSL рейтинга

Проверь качество SSL конфигурации:
https://www.ssllabs.com/ssltest/analyze.html?d=learnflow.cloud-ip.cc

Цель: **A+ рейтинг**

## Troubleshooting

### Ошибка "Address already in use"

```bash
# Найди процесс на порту 80/443:
sudo lsof -i :80
sudo lsof -i :443

# Останови его:
sudo systemctl stop nginx
# или
docker-compose down
```

### Certbot не может подключиться

```bash
# Проверь firewall:
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Проверь DNS:
dig learnflow.cloud-ip.cc +short
```

### Сертификат не обновляется

```bash
# Ручное обновление:
sudo certbot renew --dry-run

# Проверь логи:
sudo journalctl -u certbot.timer
```

## Файлы и права

```
nginx/ssl/
├── fullchain.pem  (644) - публичный сертификат
└── privkey.pem    (600) - приватный ключ
```

**Никогда не коммить эти файлы в git!** Они уже в `.gitignore`.
