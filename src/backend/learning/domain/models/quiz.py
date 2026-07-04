"""
Quiz models — LessonQuiz, QuizQuestion, QuizOption.
"""

import uuid

from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class LessonQuiz(TimestampedModel):
    """
    Short knowledge-check quiz — at most one per lesson (OneToOne).

    Defines the quiz configuration.  Student attempts and scoring live in
    the Assessment domain, which references LessonQuiz.id read-only.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField("learning.Lesson", on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    instructions = models.TextField(null=True, blank=True)
    time_limit_minutes = models.SmallIntegerField(
        null=True, blank=True, help_text="Null = untimed. Timer enforced by Assessment domain."
    )
    pass_score = models.SmallIntegerField(
        default=70,
        help_text="Percentage threshold (0–100) to pass.",
    )
    max_attempts = models.SmallIntegerField(
        null=True, blank=True, help_text="Null = unlimited retakes. Enforced by Assessment domain."
    )
    shuffle_questions = models.BooleanField(default=False)
    shuffle_options = models.BooleanField(default=False)
    show_correct_after_attempt = models.BooleanField(
        default=True,
        help_text="Show correct answers + explanations after submitting. False for high-stakes quizzes.",
    )

    class Meta:
        db_table = "courses_lessonquiz"
        verbose_name = "Lesson Quiz"
        verbose_name_plural = "Lesson Quizzes"
        constraints = [
            models.CheckConstraint(
                condition=Q(pass_score__gte=0) & Q(pass_score__lte=100),
                name="chk_quiz_pass_score",
            ),
            models.CheckConstraint(
                condition=Q(time_limit_minutes__isnull=True) | Q(time_limit_minutes__gt=0),
                name="chk_quiz_time_limit",
            ),
            models.CheckConstraint(
                condition=Q(max_attempts__isnull=True) | Q(max_attempts__gt=0),
                name="chk_quiz_max_attempts",
            ),
        ]

    def __str__(self) -> str:
        return self.title


class QuizQuestion(TimestampedModel):
    """
    Individual question within a LessonQuiz.

    Four question types:
      single_choice   – exactly one correct option  (validated at app layer)
      multiple_choice – one or more correct options
      true_false      – no QuizOption rows; handled by Assessment domain
      short_text      – no QuizOption rows; handled by Assessment domain
    """

    class Type(models.TextChoices):
        SINGLE_CHOICE = "single_choice", "Single Choice"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        TRUE_FALSE = "true_false", "True / False"
        SHORT_TEXT = "short_text", "Short Text"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        LessonQuiz, on_delete=models.CASCADE, related_name="questions", db_index=True
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    body = models.TextField(help_text="Question text. Markdown supported.")
    explanation = models.TextField(
        null=True,
        blank=True,
        help_text="Shown after answering (if show_correct_after_attempt = true).",
    )
    order = models.SmallIntegerField()
    points = models.SmallIntegerField(
        default=1, help_text="Points awarded for correct answer. Enables weighted questions."
    )

    class Meta:
        db_table = "courses_quizquestion"
        verbose_name = "Quiz Question"
        verbose_name_plural = "Quiz Questions"
        constraints = [
            models.UniqueConstraint(
                fields=["quiz_id", "order"],
                name="uq_question_quiz_order",
            ),
            models.CheckConstraint(
                condition=Q(
                    type__in=["single_choice", "multiple_choice", "true_false", "short_text"]
                ),
                name="chk_question_type",
            ),
            models.CheckConstraint(condition=Q(order__gt=0), name="chk_question_order_positive"),
            models.CheckConstraint(condition=Q(points__gt=0), name="chk_question_points_positive"),
        ]

    def __str__(self) -> str:
        return f"Q{self.order}: {self.body[:80]}"


class QuizOption(models.Model):
    """
    Answer option for choice-based questions.

    Used by: single_choice, multiple_choice, true_false.
    Not used by: short_text  (correctness handled by Assessment domain).

    Note: no updated_at — options are replaced wholesale, never patched.

    Application layer validation (not enforceable as a simple CHECK):
      single_choice → exactly one option where is_correct = True.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name="options", db_index=True
    )
    body = models.TextField()
    is_correct = models.BooleanField()
    order = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "courses_quizoption"
        verbose_name = "Quiz Option"
        verbose_name_plural = "Quiz Options"
        constraints = [
            models.UniqueConstraint(
                fields=["question_id", "order"],
                name="uq_option_question_order",
            ),
            models.CheckConstraint(
                condition=Q(order__gt=0),
                name="chk_option_order_positive",
            ),
        ]

    def __str__(self) -> str:
        marker = "✓" if self.is_correct else "✗"
        return f"[{marker}] {self.body[:80]}"
