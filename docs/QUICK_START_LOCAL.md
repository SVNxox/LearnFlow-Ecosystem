





```bash

sudo apt install postgresql redis-server


sudo -u postgres psql -c "CREATE USER learnflow WITH PASSWORD 'learnflow';"
sudo -u postgres psql -c "CREATE DATABASE learnflow_local OWNER learnflow;"


wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio && sudo mv minio /usr/local/bin/
mkdir -p ~/minio-data
```



```bash
cd /home/svn/PyCharmMiscProject/DjangoProject/LearnFlow\ Ecosystem/learnflow


python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


cp .env.local.example .env


export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py migrate
python manage.py createsuperuser
```



```bash

minio server ~/minio-data --console-address ":9001"




redis-cli ping  


export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py runserver



export DJANGO_SETTINGS_MODULE=learnflow.settings.local
celery -A learnflow worker --loglevel=info


cd src/frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm install
npm run dev

```

---



```bash



source .venv/bin/activate


minio server ~/minio-data --console-address ":9001" &


export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py runserver &


cd src/frontend && npm run dev
```

---



```bash

psql -U learnflow -d learnflow_local -h localhost -c "SELECT 1;"


redis-cli ping


curl http://localhost:8000/api/v1/health/


curl http://localhost:9000/minio/health/live


curl http://localhost:3000
```

---



```bash

python manage.py shell


python manage.py makemigrations


python manage.py migrate


python manage.py flush


redis-cli FLUSHDB


celery -A learnflow inspect active
```

---




```bash

sudo systemctl status postgresql
sudo systemctl start postgresql
```


```bash
sudo systemctl start redis
redis-cli ping
```


```bash

ps aux | grep minio

minio server ~/minio-data --console-address ":9001"
```


Это нормально! Emails печатаются в **консоль Django**.


```bash

cat src/frontend/.env.local



grep CORS .env

```

---



См. `docs/LOCAL_DEVELOPMENT_SETUP.md` для детальных инструкций.

---



| Сервис | URL | Логин |
|--------|-----|-------|
| **Backend** | http://localhost:8000 | - |
| **Frontend** | http://localhost:3000 | - |
| **Django Admin** | http://localhost:8000/admin/ | superuser |
| **API Docs** | http://localhost:8000/api/docs/ | - |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **PostgreSQL** | localhost:5432 | learnflow/learnflow |
| **Redis** | localhost:6379 | - |

---

**Готово!** 🚀 Локальное окружение запущено.
