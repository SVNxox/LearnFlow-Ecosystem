#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# LearnFlow — Create MinIO Bucket (run after first startup)
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "════════════════════════════════════════════════════════════════════════"
echo "📦 Creating MinIO bucket: learnflow-prod"
echo "════════════════════════════════════════════════════════════════════════"

# Wait for MinIO to be ready
sleep 5

# Create bucket using mc (MinIO Client)
docker compose -f docker-compose.prod.yml exec minio mc alias set local http://localhost:9000 minioadmin minioadmin123
docker compose -f docker-compose.prod.yml exec minio mc mb local/learnflow-prod --ignore-existing

echo "✅ Bucket 'learnflow-prod' created successfully"
echo ""
echo "📊 MinIO Console: http://localhost:9001"
echo "   Username: minioadmin"
echo "   Password: minioadmin123"
echo ""
