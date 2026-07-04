"""
Lesson Quiz API — управление квизами, вопросами и опциями.

Endpoints:
- GET    /api/v1/learning/lessons/{lesson_id}/quiz/ — получить квиз
- POST   /api/v1/learning/lessons/{lesson_id}/quiz/ — создать квиз
- PATCH  /api/v1/learning/lessons/{lesson_id}/quiz/ — обновить настройки
- DELETE /api/v1/learning/lessons/{lesson_id}/quiz/ — удалить квиз
- POST   /api/v1/learning/lessons/{lesson_id}/quiz/questions/ — добавить вопрос
- PATCH  /api/v1/learning/lessons/{lesson_id}/quiz/questions/{id}/ — обновить вопрос
- DELETE /api/v1/learning/lessons/{lesson_id}/quiz/questions/{id}/ — удалить вопрос
- POST   /api/v1/learning/lessons/{lesson_id}/quiz/questions/reorder/ — переупорядочить
- POST   /api/v1/learning/lessons/{lesson_id}/quiz/questions/{id}/options/ — добавить опцию
- PATCH  /api/v1/learning/lessons/{lesson_id}/quiz/questions/{id}/options/{id}/ — обновить опцию
- DELETE /api/v1/learning/lessons/{lesson_id}/quiz/questions/{id}/options/{id}/ — удалить опцию
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import (
    ManageQuizCommand,
    CreateQuizData,
    UpdateQuizSettingsData,
    AddQuestionData,
    UpdateQuestionData,
    AddOptionData,
)
from src.backend.learning.domain.models import LessonQuiz, QuizQuestion, QuizOption

logger = logging.getLogger(__name__)


def _serialize_quiz(quiz: LessonQuiz) -> dict:
    """Сериализует квиз с вопросами и опциями."""
    questions = []
    for q in quiz.questions.order_by("order"):
        options = [
            {
                "id": str(opt.id),
                "body": opt.body,
                "is_correct": opt.is_correct,
                "order": opt.order,
            }
            for opt in q.options.order_by("order")
        ]
        questions.append({
            "id": str(q.id),
            "question_type": q.question_type,
            "body": q.body,
            "explanation": q.explanation,
            "points": q.points,
            "order": q.order,
            "options": options,
        })
    return {
        "id": str(quiz.id),
        "pass_score": quiz.pass_score,
        "max_attempts": quiz.max_attempts,
        "time_limit_minutes": quiz.time_limit_minutes,
        "shuffle_questions": quiz.shuffle_questions,
        "shuffle_options": quiz.shuffle_options,
        "show_correct_answers": quiz.show_correct_answers,
        "questions": questions,
    }


class LessonQuizView(APIView):
    """GET + POST + PATCH + DELETE для квиза."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, lesson_id: str) -> Response:
        try:
            quiz = LessonQuiz.objects.prefetch_related(
                "questions__options"
            ).get(lesson_id=lesson_id)
            return Response(_serialize_quiz(quiz), status=status.HTTP_200_OK)
        except LessonQuiz.DoesNotExist:
            return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting quiz: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request, lesson_id: str) -> Response:
        data = request.data
        try:
            quiz_data = CreateQuizData(
                pass_score=data.get("pass_score", 70),
                max_attempts=data.get("max_attempts"),
                time_limit_minutes=data.get("time_limit_minutes"),
                shuffle_questions=data.get("shuffle_questions", False),
                shuffle_options=data.get("shuffle_options", False),
                show_correct_answers=data.get("show_correct_answers", True),
            )
            quiz = ManageQuizCommand.create_quiz(
                lesson_id=lesson_id, data=quiz_data, actor=request.user
            )
            return Response(_serialize_quiz(quiz), status=status.HTTP_201_CREATED)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating quiz: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request: Request, lesson_id: str) -> Response:
        """Обновляет настройки квиза (нужен quiz_id — берём из урока)."""
        try:
            quiz = LessonQuiz.objects.get(lesson_id=lesson_id)
        except LessonQuiz.DoesNotExist:
            return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        try:
            quiz_data = UpdateQuizSettingsData(
                pass_score=data.get("pass_score"),
                max_attempts=data.get("max_attempts"),
                time_limit_minutes=data.get("time_limit_minutes"),
                shuffle_questions=data.get("shuffle_questions"),
                shuffle_options=data.get("shuffle_options"),
                show_correct_answers=data.get("show_correct_answers"),
            )
            quiz = ManageQuizCommand.update_quiz_settings(
                quiz_id=str(quiz.id), data=quiz_data, actor=request.user
            )
            return Response(_serialize_quiz(quiz), status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating quiz: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, lesson_id: str) -> Response:
        try:
            quiz = LessonQuiz.objects.get(lesson_id=lesson_id)
            ManageQuizCommand.delete_quiz(quiz_id=str(quiz.id), actor=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting quiz: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizQuestionListView(APIView):
    """POST для добавления вопроса."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        try:
            quiz = LessonQuiz.objects.get(lesson_id=lesson_id)
        except LessonQuiz.DoesNotExist:
            return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        try:
            question_data = AddQuestionData(
                question_type=data.get("question_type", "single_choice"),
                body=data.get("body", ""),
                explanation=data.get("explanation"),
                points=data.get("points", 1),
            )
            question = ManageQuizCommand.add_question(
                quiz_id=str(quiz.id), data=question_data, actor=request.user
            )
            return Response({
                "id": str(question.id),
                "question_type": question.question_type,
                "body": question.body,
                "explanation": question.explanation,
                "points": question.points,
                "order": question.order,
                "options": [],
            }, status=status.HTTP_201_CREATED)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding question: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizQuestionDetailView(APIView):
    """PATCH + DELETE для вопроса."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def patch(self, request: Request, lesson_id: str, question_id: str) -> Response:
        data = request.data
        try:
            question_data = UpdateQuestionData(
                body=data.get("body"),
                explanation=data.get("explanation"),
                points=data.get("points"),
            )
            question = ManageQuizCommand.update_question(
                question_id=question_id, data=question_data, actor=request.user
            )
            return Response({
                "id": str(question.id),
                "question_type": question.question_type,
                "body": question.body,
                "explanation": question.explanation,
                "points": question.points,
                "order": question.order,
            }, status=status.HTTP_200_OK)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating question: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, lesson_id: str, question_id: str) -> Response:
        try:
            question = QuizQuestion.objects.get(id=question_id)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuizQuestion.DoesNotExist:
            return Response({"detail": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting question: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizQuestionReorderView(APIView):
    """POST для переупорядочивания вопросов."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        question_ids = request.data.get("question_ids", [])
        try:
            
            for order, qid in enumerate(question_ids, start=1):
                QuizQuestion.objects.filter(id=qid).update(order=order)
            return Response({"detail": "Questions reordered"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error reordering questions: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizOptionListView(APIView):
    """POST для добавления опции."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str, question_id: str) -> Response:
        data = request.data
        try:
            option_data = AddOptionData(
                body=data.get("body", ""),
                is_correct=data.get("is_correct", False),
            )
            option = ManageQuizCommand.add_option(
                question_id=question_id, data=option_data, actor=request.user
            )
            return Response({
                "id": str(option.id),
                "body": option.body,
                "is_correct": option.is_correct,
                "order": option.order,
            }, status=status.HTTP_201_CREATED)
        except (BusinessValidationError, NotFoundError, AccessDeniedError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding option: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizOptionDetailView(APIView):
    """PATCH + DELETE для опции."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def patch(self, request: Request, lesson_id: str, question_id: str, option_id: str) -> Response:
        data = request.data
        try:
            option = QuizOption.objects.get(id=option_id)
            if "body" in data:
                option.body = data["body"]
            if "is_correct" in data:
                option.is_correct = data["is_correct"]
            option.save()
            return Response({
                "id": str(option.id),
                "body": option.body,
                "is_correct": option.is_correct,
                "order": option.order,
            }, status=status.HTTP_200_OK)
        except QuizOption.DoesNotExist:
            return Response({"detail": "Option not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating option: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, lesson_id: str, question_id: str, option_id: str) -> Response:
        try:
            option = QuizOption.objects.get(id=option_id)
            option.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuizOption.DoesNotExist:
            return Response({"detail": "Option not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting option: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)