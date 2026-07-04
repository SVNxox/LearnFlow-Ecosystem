



#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════════════"
echo "🚀 LearnFlow Production Startup"
echo "════════════════════════════════════════════════════════════════════════"




echo "⏳ Waiting for PostgreSQL..."
until python -c "import psycopg; psycopg.connect('${DATABASE_URL}').close()" 2>/dev/null; do
  echo "   Database not ready, retrying in 2s..."
  sleep 2
done
echo "✓ PostgreSQL is ready"




echo ""
echo "📊 Running database migrations..."
python manage.py migrate --noinput
echo "✓ Migrations applied"




echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected"




if [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo ""
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" || echo "⚠ Superuser already exists"
fi




echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ Startup complete. Starting Gunicorn..."
echo "════════════════════════════════════════════════════════════════════════"
echo ""

exec "$@"
