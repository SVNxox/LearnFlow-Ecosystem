#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# LearnFlow — Deploy to Production Server
# ═══════════════════════════════════════════════════════════════════════════
# Usage: ./deploy.sh user@server_ip
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Check arguments
if [ -z "$1" ]; then
    echo "❌ Usage: ./deploy.sh user@server_ip"
    echo "   Example: ./deploy.sh root@192.168.1.100"
    exit 1
fi

SERVER=$1
REMOTE_PATH="/opt/learnflow"

echo "════════════════════════════════════════════════════════════════════════"
echo "🚀 LearnFlow Production Deployment"
echo "════════════════════════════════════════════════════════════════════════"
echo "Server: $SERVER"
echo "Remote path: $REMOTE_PATH"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Create remote directory
echo "📁 Creating remote directory..."
ssh $SERVER "mkdir -p $REMOTE_PATH"

# Upload files via rsync
echo "📤 Uploading files..."
rsync -avz --progress \
  --exclude='.venv' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='.pytest_cache' \
  --exclude='.idea' \
  --exclude='staticfiles' \
  --exclude='media' \
  --exclude='logs' \
  --exclude='*.log' \
  --exclude='.env' \
  --exclude='.env.local' \
  --exclude='.env.backup' \
  --exclude='node_modules' \
  --exclude='.DS_Store' \
  --exclude='*.swp' \
  . $SERVER:$REMOTE_PATH/

echo ""
echo "✅ Files uploaded successfully"
echo ""

# Set permissions on server
echo "🔧 Setting permissions..."
ssh $SERVER "cd $REMOTE_PATH && chmod +x entrypoint.sh create_minio_bucket.sh run_celery.sh 2>/dev/null || true"

# Create necessary directories
echo "📁 Creating directories..."
ssh $SERVER "cd $REMOTE_PATH && mkdir -p nginx/ssl nginx/logs logs backups media staticfiles"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ Deployment completed successfully!"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "📝 Next steps on server:"
echo ""
echo "1. SSH to server:"
echo "   ssh $SERVER"
echo ""
echo "2. Navigate to project:"
echo "   cd $REMOTE_PATH"
echo ""
echo "3. Check .env.production:"
echo "   cat .env.production"
echo ""
echo "4. Start services:"
echo "   docker compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "5. Check logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "6. Create MinIO bucket:"
echo "   ./create_minio_bucket.sh"
echo ""
echo "7. Create superuser:"
echo "   docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
