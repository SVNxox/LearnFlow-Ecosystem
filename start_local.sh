



set -e


GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 LearnFlow — Local Development Startup${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"


if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Ошибка: запустите скрипт из корневой директории проекта${NC}"
    exit 1
fi


echo -e "\n${YELLOW}📊 Проверка PostgreSQL...${NC}"
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL запущен${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL не запущен, запускаю...${NC}"
    sudo systemctl start postgresql
    echo -e "${GREEN}✓ PostgreSQL запущен${NC}"
fi


if psql -U learnflow -d learnflow_local -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ База данных доступна${NC}"
else
    echo -e "${RED}❌ База данных недоступна. Создайте БД командой:${NC}"
    echo -e "   sudo -u postgres psql -c \"CREATE USER learnflow WITH PASSWORD 'learnflow';\""
    echo -e "   sudo -u postgres psql -c \"CREATE DATABASE learnflow_local OWNER learnflow;\""
    exit 1
fi


echo -e "\n${YELLOW}📮 Проверка Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis запущен и доступен${NC}"
else
    echo -e "${YELLOW}⚠ Redis не отвечает, пытаюсь запустить через systemd...${NC}"
    if sudo systemctl start redis 2>/dev/null || sudo systemctl start redis-server 2>/dev/null; then
        sleep 2
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis запущен${NC}"
        else
            echo -e "${RED}❌ Redis запущен, но не отвечает${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Не удалось запустить Redis через systemd${NC}"
        echo -e "${YELLOW}💡 Попробуйте запустить вручную: redis-server &${NC}"
        exit 1
    fi
fi


echo -e "\n${YELLOW}🗄️  Проверка MinIO...${NC}"
if pgrep -x "minio" > /dev/null; then
    echo -e "${GREEN}✓ MinIO уже запущен${NC}"
else
    echo -e "${YELLOW}⚠ MinIO не запущен, запускаю...${NC}"
    if [ ! -d "$HOME/minio-data" ]; then
        mkdir -p "$HOME/minio-data"
    fi
    nohup minio server "$HOME/minio-data" --console-address ":9001" > minio.log 2>&1 &
    sleep 2
    echo -e "${GREEN}✓ MinIO запущен (http://localhost:9001)${NC}"
    echo -e "${YELLOW}  Логин: minioadmin / minioadmin${NC}"
fi


echo -e "\n${YELLOW}🐍 Проверка Python окружения...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Виртуальное окружение не найдено, создаю...${NC}"
    python3.12 -m venv .venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Виртуальное окружение активировано${NC}"


if [ ! -f ".venv/.dependencies_installed" ]; then
    echo -e "\n${YELLOW}📦 Установка зависимостей...${NC}"
    pip install -q -r requirements.txt
    touch .venv/.dependencies_installed
    echo -e "${GREEN}✓ Зависимости установлены${NC}"
else
    echo -e "${GREEN}✓ Зависимости уже установлены${NC}"
fi


echo -e "\n${YELLOW}🔄 Проверка миграций...${NC}"
export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py migrate --check > /dev/null 2>&1 || {
    echo -e "${YELLOW}⚠ Применяю миграции...${NC}"
    python manage.py migrate
}
echo -e "${GREEN}✓ Миграции применены${NC}"


echo -e "\n${YELLOW}🌐 Запуск Django dev server...${NC}"
export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py runserver > django.log 2>&1 &
DJANGO_PID=$!
sleep 2

if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Django запущен (http://localhost:8000)${NC}"
    echo -e "${GREEN}  PID: $DJANGO_PID${NC}"
else
    echo -e "${RED}❌ Django не запустился, проверьте django.log${NC}"
    exit 1
fi


echo -e "\n${YELLOW}⚙️  Запуск Celery worker...${NC}"
export DJANGO_SETTINGS_MODULE=learnflow.settings.local
celery -A learnflow worker -Q celery,email,notifications --loglevel=info > celery.log 2>&1 &
CELERY_PID=$!
sleep 2
echo -e "${GREEN}✓ Celery worker запущен (слушает все очереди)${NC}"
echo -e "${GREEN}  PID: $CELERY_PID${NC}"


echo -e "\n${YELLOW}🤖 Проверка Telegram Bot...${NC}"
export DJANGO_SETTINGS_MODULE=learnflow.settings.local
TELEGRAM_BOT_PID=""
BOT_USERNAME=""


if [ -f ".env" ]; then
    BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" | xargs)
    BOT_USERNAME=$(grep "^TELEGRAM_BOT_USERNAME=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" | xargs)

    if [ ! -z "$BOT_TOKEN" ]; then
        echo -e "${YELLOW}🚀 Запуск Telegram бота...${NC}"
        python manage.py run_bot > telegram_bot.log 2>&1 &
        TELEGRAM_BOT_PID=$!
        sleep 2


        if ps -p $TELEGRAM_BOT_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Telegram бот запущен${NC}"
            echo -e "${GREEN}  PID: $TELEGRAM_BOT_PID${NC}"
            if [ ! -z "$BOT_USERNAME" ]; then
                echo -e "${GREEN}  Username: @$BOT_USERNAME${NC}"
            fi
        else
            echo -e "${RED}❌ Telegram бот не запустился, проверьте telegram_bot.log${NC}"
            TELEGRAM_BOT_PID=""
        fi
    else
        echo -e "${YELLOW}⚠ TELEGRAM_BOT_TOKEN не найден или пустой${NC}"
        echo -e "${YELLOW}  💡 Добавьте TELEGRAM_BOT_TOKEN в .env для запуска бота${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Файл .env не найден, пропускаю запуск бота${NC}"
fi


echo -e "\n${YELLOW}💻 Проверка Frontend...${NC}"
FRONTEND_PID=""
if [ -d "src/frontend" ]; then
    cd src/frontend

    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠ Установка npm зависимостей...${NC}"
        npm install
    fi

    if [ ! -f ".env.local" ]; then
        echo -e "${YELLOW}⚠ Создаю .env.local...${NC}"
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
    fi

    echo -e "${YELLOW}🚀 Запуск Next.js dev server...${NC}"
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..
    sleep 3
    echo -e "${GREEN}✓ Frontend запущен (http://localhost:3000)${NC}"
    echo -e "${GREEN}  PID: $FRONTEND_PID${NC}"
else
    echo -e "${YELLOW}⚠ Frontend директория не найдена, пропускаю...${NC}"
fi


echo "$DJANGO_PID" > .django.pid
echo "$CELERY_PID" > .celery.pid
[ ! -z "$FRONTEND_PID" ] && echo "$FRONTEND_PID" > .frontend.pid
[ ! -z "$TELEGRAM_BOT_PID" ] && echo "$TELEGRAM_BOT_PID" > .telegram_bot.pid


echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ LearnFlow запущен успешно!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e ""
echo -e "${YELLOW}📌 Запущенные сервисы:${NC}"
echo -e "   🌐 Backend:       http://localhost:8000"
echo -e "   💻 Frontend:      http://localhost:3000"
echo -e "   🔐 Django Admin:  http://localhost:8000/admin/"
echo -e "   📚 API Docs:      http://localhost:8000/api/docs/"
echo -e "   🗄️  MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"

if [ ! -z "$TELEGRAM_BOT_PID" ]; then
    if [ ! -z "$BOT_USERNAME" ]; then
        echo -e "   🤖 Telegram Bot:  https://t.me/$BOT_USERNAME"
    else
        echo -e "   🤖 Telegram Bot:  Запущен (PID: $TELEGRAM_BOT_PID)"
    fi
else
    echo -e "   🤖 Telegram Bot:  ${RED}Не запущен${NC}"
fi

echo -e ""
echo -e "${YELLOW}📊 Логи:${NC}"
echo -e "   Django:       tail -f django.log"
echo -e "   Celery:       tail -f celery.log"
echo -e "   Frontend:     tail -f frontend.log"
echo -e "   MinIO:        tail -f minio.log"

if [ ! -z "$TELEGRAM_BOT_PID" ]; then
    echo -e "   Telegram Bot: tail -f telegram_bot.log"
fi

echo -e ""
echo -e "${YELLOW}🛑 Остановить:${NC}"
echo -e "   ./stop_local.sh"
echo -e ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"