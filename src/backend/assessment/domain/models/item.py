"""
AssessmentItem Model

Individual question/task within an assessment.
Supports: single_choice, multiple_choice, text_answer, coding, project, interview.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class AssessmentItem(models.Model):
    """
    Assessment Item — вопрос или задание.

    Type определяет метод оценивания:
    - single_choice, multiple_choice → auto-graded instantly
    - coding → auto-graded async (sandbox execution)
    - text_answer, project, interview → mentor review required
    """

    class ItemType(models.TextChoices):
        SINGLE_CHOICE = 'single_choice', 'Single Choice'
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        TEXT_ANSWER = 'text_answer', 'Text Answer'
        CODING = 'coding', 'Coding Task'
        PROJECT = 'project', 'Project Task'
        INTERVIEW = 'interview', 'Interview Question'

    class PartialCreditStrategy(models.TextChoices):
        ALL_OR_NOTHING = 'all_or_nothing', 'All or Nothing'
        PROPORTIONAL = 'proportional', 'Proportional'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    assessment = models.ForeignKey(
        'assessment.ModuleAssessment',
        on_delete=models.CASCADE,
        related_name='items'
    )

    type = models.CharField(
        max_length=20,
        choices=ItemType.choices
    )

    order = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Display order (1, 2, 3...)"
    )

    title = models.TextField(
        help_text="Question text or task description"
    )

    description = models.TextField(
        blank=True,
        help_text="Additional context or instructions"
    )

    max_points = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Maximum points for this item"
    )

    partial_credit_strategy = models.CharField(
        max_length=20,
        choices=PartialCreditStrategy.choices,
        default=PartialCreditStrategy.ALL_OR_NOTHING,
        help_text="How to award partial credit (for multiple_choice and coding)"
    )

    explanation = models.TextField(
        blank=True,
        help_text="Shown after grading (why answer is correct/wrong)"
    )

    mentor_review_required = models.BooleanField(
        default=False,
        help_text="TRUE for text_answer, project, interview"
    )

    coding_language = models.CharField(
        max_length=30,
        blank=True,
        help_text="python, javascript, java, etc."
    )

    starter_code = models.TextField(
        blank=True,
        help_text="Pre-filled code template"
    )

    sample_answer = models.TextField(
        blank=True,
        help_text="Reference answer for mentor (text_answer type)"
    )

    min_word_count = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Minimum words required (text_answer)"
    )

    submission_requirements = models.TextField(
        blank=True,
        help_text="Project requirements checklist"
    )

    class Meta:
        db_table = 'assessment_assessmentitem'
        indexes = [
            models.Index(fields=['assessment', 'order'], name='idx_item_assess_order'),
            models.Index(fields=['type'], name='idx_item_type'),
        ]
        ordering = ['assessment', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'order'],
                name='uq_item_assess_order'
            )
        ]

    def __str__(self):
        return f"Item {self.order}: {self.title[:50]}"

    def save(self, *args, **kwargs):
        """Set mentor_review_required based on type."""
        if self.type in [
            self.ItemType.TEXT_ANSWER,
            self.ItemType.PROJECT,
            self.ItemType.INTERVIEW
        ]:
            self.mentor_review_required = True
        super().save(*args, **kwargs)
