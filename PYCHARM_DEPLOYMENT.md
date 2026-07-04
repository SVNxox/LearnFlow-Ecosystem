# ═══════════════════════════════════════════════════════════════════════════
# PyCharm Deployment Configuration
# ═══════════════════════════════════════════════════════════════════════════
# Инструкция по настройке PyCharm для деплоя на сервер
# ═══════════════════════════════════════════════════════════════════════════

## Шаг 1: Открой настройки Deployment

1. В PyCharm: **Tools → Deployment → Configuration**
2. Нажми **"+"** → **SFTP**
3. Name: **LearnFlow Production**

---

## Шаг 2: Настрой Connection

**Вкладка "Connection":**

```
Type: SFTP
Host: твой_сервер_ip (например: 192.168.1.100)
Port: 22
Root path: /opt/learnflow

User name: твой_пользователь (например: root)
Auth type: 
  - Key pair (рекомендуется) — выбери свой SSH ключ
  - Password — введи пароль

✓ Test Connection — проверь подключение
```

---

## Шаг 3: Настрой Mappings

**Вкладка "Mappings":**

```
Local path: /home/svn/PyCharmMiscProject/DjangoProject/LearnFlow Ecosystem/learnflow
Deployment path: /
Web path: /
```

---

## Шаг 4: Исключи ненужные файлы

**Вкладка "Excluded Paths":**

Нажми **"+"** и добавь:

```
.venv
.git
__pycache__
*.pyc
*.pyo
.pytest_cache
.idea
staticfiles
media
logs
*.log
.env
.env.local
.DS_Store
node_modules
postgres_data
```

---

## Шаг 5: Настрой автоматическую загрузку (опционально)

**Вкладка "Options":**

```
✓ Upload changed files automatically to the default server: On explicit save action

Это автоматически загрузит файлы на сервер при сохранении (Ctrl+S)
```

---

## Шаг 6: Загрузи проект

**3 способа:**

### Способ 1: Загрузить весь проект
1. ПКМ на корень проекта (learnflow)
2. **Deployment → Upload to LearnFlow Production**

### Способ 2: Загрузить отдельные файлы
1. ПКМ на файл/папку
2. **Deployment → Upload to LearnFlow Production**

### Способ 3: Сравнить и загрузить изменения
1. **Tools → Deployment → Sync with Deployed to LearnFlow Production**
2. Проверь что будет загружено
3. Нажми **Sync**

---

## Проверка загруженных файлов

**Tools → Deployment → Browse Remote Host**

Появится окно с файловой системой сервера.
Проверь что все файлы загрузились в `/opt/learnflow/`

---

## После загрузки

### На сервере выполни:

```bash
# SSH к серверу
ssh user@server_ip

# Перейди в папку
cd /opt/learnflow

# Проверь что файлы загрузились
ls -la

# Установи права на скрипты
chmod +x entrypoint.sh create_minio_bucket.sh

# Создай нужные папки
mkdir -p nginx/ssl nginx/logs logs backups

# Запусти
docker compose -f docker-compose.prod.yml up -d --build

# Проверь логи
docker compose -f docker-compose.prod.yml logs -f
```

---

## Troubleshooting

### Permission denied

Если появляется **Permission denied**:

```bash
# На сервере:
sudo chown -R $USER:$USER /opt/learnflow
```

### Connection refused

Проверь:
1. Сервер доступен: `ping server_ip`
2. SSH работает: `ssh user@server_ip`
3. Порт 22 открыт в firewall

### Files not uploading

1. Проверь "Excluded Paths" — убедись что файлы не исключены
2. Попробуй: **Tools → Deployment → Upload to LearnFlow Production → Force Upload**

---

## Горячие клавиши

```
Ctrl+Shift+Alt+X — Quick Upload
Ctrl+Alt+Shift+S — Sync with Deployed
```

---

## Быстрый деплой через скрипт (альтернатива)

Если PyCharm не работает, используй скрипт:

```bash
./deploy.sh user@server_ip
```

Пример:
```bash
./deploy.sh root@192.168.1.100
```

---

## Checklist перед деплоем

- [ ] `.env.production` заполнен всеми секретами
- [ ] `docker-compose.prod.yml` настроен
- [ ] `nginx/conf.d/learnflow.conf` содержит правильный домен
- [ ] SSL сертификаты готовы (или будут созданы на сервере)
- [ ] Проверен список excluded paths

---

**Готово!** Теперь можно деплоить через PyCharm одним кликом.
