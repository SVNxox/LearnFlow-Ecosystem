"""
Learning REST API — Main Router.

API Structure:
/api/learning/              - Course endpoints
/api/learning/modules/      - Module endpoints
/api/learning/lessons/      - Lesson endpoints
"""

from django.urls import path, include

app_name = "learning"

urlpatterns = [
    path("learning/", include("learning.presentation.rest.courses.urls")),
    path("learning/modules/", include("learning.presentation.rest.modules.urls")),
    path("learning/lessons/", include("learning.presentation.rest.lessons.urls")),
]
