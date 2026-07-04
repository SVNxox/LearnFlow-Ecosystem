"""
Health check and system status endpoints
"""
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'service': 'learnflow',
        'version': '1.0.0'
    })


def readiness_check(request):
    """Readiness probe for Kubernetes"""
    
    return JsonResponse({
        'status': 'ready',
        'database': 'connected'
    })


urlpatterns = [
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='readiness'),
]
