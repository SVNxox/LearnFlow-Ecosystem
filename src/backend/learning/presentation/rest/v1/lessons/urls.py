"""
Lesson REST API URLs.

Важно: статические пути (upload-url/, reorder/) должны идти ПЕРЕД
динамическими (<str:id>/), иначе Django перехватит их как id.
"""

from django.urls import path

from .content_upload import LessonContentUploadUrlView, LessonContentPublicUrlView
from .create import LessonCreateView
from .detail import LessonDetailView
from .list import LessonListView
from .publish import LessonPublishView, LessonUnpublishView
from .reorder import LessonReorderView


from .content import LessonContentListView, LessonContentDetailView, LessonContentReorderView


from .homework import LessonHomeworkView


from .practice import LessonPracticeListView, LessonPracticeDetailView, LessonPracticeReorderView


from .quiz import (
    LessonQuizView,
    QuizQuestionListView,
    QuizQuestionDetailView,
    QuizQuestionReorderView,
    QuizOptionListView,
    QuizOptionDetailView,
)

urlpatterns = [
    
    path("", LessonListView.as_view(), name="lesson-list"),
    path("create/", LessonCreateView.as_view(), name="lesson-create"),

    
    path("<str:lesson_id>/", LessonDetailView.as_view(), name="lesson-detail"),

    
    path("<str:lesson_id>/publish/", LessonPublishView.as_view(), name="lesson-publish"),
    path("<str:lesson_id>/unpublish/", LessonUnpublishView.as_view(), name="lesson-unpublish"),

    
    path("reorder/", LessonReorderView.as_view(), name="lesson-reorder"),

    
    
    path("<str:lesson_id>/content/upload-url/", LessonContentUploadUrlView.as_view(), name="lesson-content-upload-url"),
    path("<str:lesson_id>/content/reorder/", LessonContentReorderView.as_view(), name="lesson-content-reorder"),
    path("<str:lesson_id>/content/", LessonContentListView.as_view(), name="lesson-content-list"),
    path("<str:lesson_id>/content/<str:content_id>/", LessonContentDetailView.as_view(), name="lesson-content-detail"),

    
    path("content/url/", LessonContentPublicUrlView.as_view(), name="lesson-content-public-url"),

    
    path("<str:lesson_id>/homework/", LessonHomeworkView.as_view(), name="lesson-homework"),

    
    
    path("<str:lesson_id>/practice/reorder/", LessonPracticeReorderView.as_view(), name="lesson-practice-reorder"),
    path("<str:lesson_id>/practice/", LessonPracticeListView.as_view(), name="lesson-practice-list"),
    path("<str:lesson_id>/practice/<str:practice_id>/", LessonPracticeDetailView.as_view(), name="lesson-practice-detail"),

    
    
    path("<str:lesson_id>/quiz/", LessonQuizView.as_view(), name="lesson-quiz"),
    path("<str:lesson_id>/quiz/questions/reorder/", QuizQuestionReorderView.as_view(), name="quiz-question-reorder"),
    path("<str:lesson_id>/quiz/questions/", QuizQuestionListView.as_view(), name="quiz-question-list"),
    path("<str:lesson_id>/quiz/questions/<str:question_id>/", QuizQuestionDetailView.as_view(), name="quiz-question-detail"),
    path("<str:lesson_id>/quiz/questions/<str:question_id>/options/", QuizOptionListView.as_view(), name="quiz-option-list"),
    path("<str:lesson_id>/quiz/questions/<str:question_id>/options/<str:option_id>/", QuizOptionDetailView.as_view(), name="quiz-option-detail"),
]