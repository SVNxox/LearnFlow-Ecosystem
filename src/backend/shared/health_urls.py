"""
src/backend/shared/health_urls.py

/health/       — liveness probe (process is running)
/health/ready/ — readiness probe (DB + cache are reachable)
"""
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import path
from django.utils import timezone


def health_live(request):
    return JsonResponse({"status": "ok", "timestamp": timezone.now().isoformat()})


def health_ready(request):
    checks = {}
    overall = "ok"

    
    try:
        connection.ensure_connection()
        checks["db"] = "ok"
    except Exception as exc:
        checks["db"] = f"error: {exc}"
        overall = "error"

    
    try:
        cache.set("health_check", "1", timeout=5)
        assert cache.get("health_check") == "1"
        checks["cache"] = "ok"
    except Exception as exc:
        checks["cache"] = f"error: {exc}"
        overall = "error"

    status_code = 200 if overall == "ok" else 503
    return JsonResponse({"status": overall, "checks": checks}, status=status_code)


urlpatterns = [
    path("health/",       health_live,  name="health-live"),
    path("health/ready/", health_ready, name="health-ready"),
]
