"""
CodingTestCase Model

Test cases for coding type items.
Used for automatic code grading.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class CodingTestCase(models.Model):
    """
    Coding Test Case — тест-кейс для coding item.

    Используется для автоматической проверки кода:
    - input → stdin или аргументы функции
    - expected_output → сравнивается с actual output
    - points → вес этого теста (NULL = равное распределение)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    item = models.ForeignKey(
        'assessment.AssessmentItem',
        on_delete=models.CASCADE,
        related_name='test_cases'
    )

    input = models.TextField(
        help_text="stdin input or function arguments"
    )

    expected_output = models.TextField(
        help_text="Expected output (compared with actual)"
    )

    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Points for this test case (NULL = equal distribution)"
    )

    time_limit_ms = models.IntegerField(
        default=2000,
        validators=[MinValueValidator(100)],
        help_text="Execution time limit in milliseconds"
    )

    memory_limit_mb = models.IntegerField(
        default=128,
        validators=[MinValueValidator(16)],
        help_text="Memory limit in megabytes"
    )

    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden test cases are not shown to student"
    )

    is_sample = models.BooleanField(
        default=False,
        help_text="Sample test cases shown in problem description"
    )

    order = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Execution order"
    )

    class Meta:
        db_table = 'assessment_codingtestcase'
        indexes = [
            models.Index(fields=['item', 'order'], name='idx_testcase_item_order'),
            models.Index(fields=['is_sample'], name='idx_testcase_sample'),
        ]
        ordering = ['item', 'order']

    def __str__(self):
        visibility = 'sample' if self.is_sample else ('hidden' if self.is_hidden else 'visible')
        return f"TestCase {self.order} ({visibility})"
