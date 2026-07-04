from django.urls import path
from .detail import PracticeDetailView, PracticeSubmitView

urlpatterns = [
    path("<str:practice_id>/", PracticeDetailView.as_view(), name="practice-detail"),
    path("<str:practice_id>/submit/", PracticeSubmitView.as_view(), name="practice-submit"),
]