



set -e


GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🛑 LearnFlow — Stopping Local Development${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"


stop_process() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⏹  Останавливаю $service_name (PID: $PID)...${NC}"
            kill "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null
            rm "$pid_file"
            echo -e "${GREEN}✓ $service_name остановлен${NC}"
        else
            echo -e "${YELLOW}⚠ $service_name уже остановлен${NC}"
            rm "$pid_file"
        fi
    else
        echo -e "${YELLOW}⚠ PID файл $pid_file не найден${NC}"
    fi
}


echo -e "\n${YELLOW}🌐 Останавливаю Django...${NC}"
stop_process ".django.pid" "Django"


pkill -f "manage.py runserver" 2>/dev/null && echo -e "${GREEN}✓ Django runserver processes killed${NC}" || true


echo -e "\n${YELLOW}⚙️  Останавливаю Celery...${NC}"
stop_process ".celery.pid" "Celery"


pkill -f "celery -A learnflow worker" 2>/dev/null && echo -e "${GREEN}✓ Celery worker processes killed${NC}" || true
pkill -f "celery -A learnflow beat" 2>/dev/null && echo -e "${GREEN}✓ Celery beat processes killed${NC}" || true


echo -e "\n${YELLOW}🤖 Останавливаю Telegram Bot...${NC}"
stop_process ".telegram_bot.pid" "Telegram Bot"


pkill -f "manage.py run_bot" 2>/dev/null && echo -e "${GREEN}✓ Telegram bot processes killed${NC}" || true


echo -e "\n${YELLOW}💻 Останавливаю Frontend...${NC}"
stop_process ".frontend.pid" "Frontend"


pkill -f "next dev" 2>/dev/null && echo -e "${GREEN}✓ Next.js dev processes killed${NC}" || true






echo -e "\n${YELLOW}🧹 Очистка логов?${NC}"
read -p "Удалить лог файлы? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f django.log celery.log frontend.log minio.log telegram_bot.log
    echo -e "${GREEN}✓ Логи удалены${NC}"
else
    echo -e "${YELLOW}⚠ Логи сохранены${NC}"
fi


echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Все сервисы остановлены${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e ""
echo -e "${YELLOW}📝 Примечание:${NC}"
echo -e "   PostgreSQL и Redis продолжают работать (системные сервисы)"
echo -e "   MinIO продолжает работать (опционально остановить: pkill minio)"
echo -e ""
echo -e "${YELLOW}🚀 Для запуска снова:${NC}"
echo -e "   ./start_local.sh"
echo -e ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"