

Образовательная платформа для онлайн и офлайн обучения.



```bash
git clone https://github.com/your-org/learnflow
cd learnflow
cp .env.example .env
docker-compose up -d
python manage.py migrate
python manage.py runserver
```



Начни с чтения [`CLAUDE.md`](./CLAUDE.md) — там карта проекта, паттерны и правила.



| Раздел               | Файл                        |
|----------------------|-----------------------------|
| Архитектура системы  | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Решения и ADR        | [docs/DECISIONS.md](docs/DECISIONS.md)       |
| База данных          | [docs/DATABASE.md](docs/DATABASE.md)         |
| Бизнес-домен         | [docs/DOMAIN.md](docs/DOMAIN.md)             |
| API                  | [docs/API.md](docs/API.md)                   |
| Деплой               | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)     |
| Безопасность         | [docs/SECURITY.md](docs/SECURITY.md)         |
| Дорожная карта       | [docs/ROADMAP.md](docs/ROADMAP.md)           |
| Контрибьютинг        | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |



- **Backend:** Python 3.12, Django 5.x, Django REST Framework
- **База данных:** PostgreSQL 16
- **Очередь задач:** Celery + Redis
- **Аутентификация:** JWT (djangorestframework-simplejwt)
- **Документация API:** drf-spectacular (OpenAPI 3)



Proprietary — LearnFlow Team



Прочти CLAUDE.md, DOMAIN.md, ARCHITECTURE.md, DATABASE.md, API.md, SECURITY.md, DEPLOYMENT.md, CONTRIBUTING.md, DECISIONS.md, ROADMAP.md и скажи свои пониманию о проекте и если что я тебе подправлю

Прочти CLAUDE.md и скажи свои пониманию о проекте и если что я тебе подправлю


curl -v -X POST https://chat.qwen.ai/v1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImJiNDcyNzI5LWIzNzQtNDk3Ny04YzJlLTlkMzliNDE3NDY3NiIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzc4MTYyNTc4LCJleHAiOjE3ODMzNzg2NTd9.aFsav3FHrbFUAinpGlDmd6zXgPOrzDYHzdW4IX_z938" \
  -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0" \
  -H "Referer: https://chat.qwenlm.ai/" \
  -H "Origin: https://chat.qwenlm.ai" \
  -d '{"model":"qwen3-max","messages":[{"role":"user","content":"hi"}]}'


cc() {
    export ANTHROPIC_BASE_URL="http://localhost:20128/v1"
    export ANTHROPIC_API_KEY="dummy"
    export ANTHROPIC_SMALL_FAST_MODEL="ds-web/deepseek-v4-flash-think"
    export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

    case "$1" in
        sonnet)
            export ANTHROPIC_MODEL="kr/claude-sonnet-4.5"
            echo "Using model: kr/claude-sonnet-4.5"
            ;;
        coder)
            export ANTHROPIC_MODEL="kr/qwen3-coder-next"
            echo "Using model: kr/qwen3-coder-next"
            ;;
        think)
            export ANTHROPIC_MODEL="ds-web/deepseek-v4-pro-think"
            echo "Using model: ds-web/deepseek-v4-pro-think"
            ;;
        search)
            export ANTHROPIC_MODEL="ds-web/deepseek-v4-pro-think-search"
            echo "Using model: ds-web/deepseek-v4-pro-think-search"
            ;;
        fastcc)
            export ANTHROPIC_MODEL="kr/claude-haiku-4.5"
            echo "Using model: kr/claude-haiku-4.5"
            ;;
        fastds)
            export ANTHROPIC_MODEL="ds-web/deepseek-v4-flash-think"
            echo "Using model: ds-web/deepseek-v4-flash-think"
            ;;
        *)
            echo "Usage: cc {sonnet|coder|think|search|fastcc|fastds}"
            echo
            echo "  sonnet  -> kr/claude-sonnet-4.5"
            echo "  coder   -> kr/qwen3-coder-next"
            echo "  think   -> ds-web/deepseek-v4-pro-think"
            echo "  search  -> ds-web/deepseek-v4-pro-think-search"
            echo "  fastcc  -> kr/claude-haiku-4.5"
            echo "  fastds  -> ds-web/deepseek-v4-flash-think"
            return 1
            ;;
    esac

    shift
    command claude "$@"
}