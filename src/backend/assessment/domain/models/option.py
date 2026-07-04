"""
AssessmentOption Model

Answer options for single_choice and multiple_choice items.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator


class AssessmentOption(models.Model):
    """
    Assessment Option — вариант ответа для choice items.

    Используется только для:
    - single_choice (один правильный)
    - multiple_choice (несколько правильных)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    item = models.ForeignKey(
        'assessment.AssessmentItem',
        on_delete=models.CASCADE,
        related_name='options'
    )

    text = models.TextField(
        help_text="Option text"
    )

    is_correct = models.BooleanField(
        default=False,
        help_text="TRUE if this is a correct answer"
    )

    order = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Display order"
    )

    explanation = models.TextField(
        blank=True,
        help_text="Shown after grading (why this option is correct/incorrect)"
    )

    class Meta:
        db_table = 'assessment_assessmentoption'
        indexes = [
            models.Index(fields=['item', 'order'], name='idx_opt_item_order'),
        ]
        ordering = ['item', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['item', 'order'],
                name='uq_opt_item_order'
            )
        ]

    def __str__(self):
        return f"Option {self.order}: {self.text[:50]}"
