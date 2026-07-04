"""
Learning Domain REST API v1 — Main Router

According to ADR-034: Domain-Prefixed URLs
Structure: /api/v1/learning/{feature}/{action}/
"""

from django.urls import path, include

app_name = "learning_v1"

urlpatterns = [
    path("courses/", include("src.backend.learning.presentation.rest.v1.courses.urls")),
    path("modules/", include("src.backend.learning.presentation.rest.v1.modules.urls")),
    path("lessons/", include("src.backend.learning.presentation.rest.v1.lessons.urls")),
    path("admin/", include("src.backend.learning.presentation.rest.v1.admin.urls")),
    path("categories/", include("src.backend.learning.presentation.rest.v1.categories.urls")),
    path("practice/", include("src.backend.learning.presentation.rest.v1.practice.urls")),
]
