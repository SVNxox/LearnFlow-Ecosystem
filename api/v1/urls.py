"""
API v1 URL Configuration

Domain-prefixed URLs according to ADR-034.
Structure: /api/v1/{domain}/{feature}/{action}/
"""
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
urlpatterns = [
    path('identity/', include('src.backend.identity.presentation.rest.v1.urls')),
    path('learning/', include('src.backend.learning.presentation.rest.v1.urls')),
    path('progress/', include('src.backend.progress.presentation.rest.v1.urls')),
    path('assessment/', include('src.backend.assessment.presentation.rest.v1.urls')),
    path('enrollment/', include('src.backend.enrollment.presentation.rest.urls')),
    path('certificates/', include('src.backend.certificates.presentation.rest.v1.urls')),
    path('mentorship/', include('src.backend.mentorship.presentation.rest.v1.urls')),
    path('payment/', include('src.backend.payment.presentation.rest.v1.urls')),
    path('submissions/', include('src.backend.submissions.presentation.rest.v1.urls')),

    
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
