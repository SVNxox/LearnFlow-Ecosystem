


cd "$(dirname "$0")"

echo "🚀 Starting Celery worker with local settings..."
echo "📧 Emails will be printed to THIS console"
echo "📮 Listening to queues: celery, email, notifications"
echo ""

export DJANGO_SETTINGS_MODULE=learnflow.settings.local
source .venv/bin/activate

celery -A learnflow worker -Q celery,email,notifications --loglevel=info
