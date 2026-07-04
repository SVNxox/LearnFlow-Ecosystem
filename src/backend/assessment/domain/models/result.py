"""
CodingTestCaseResult Model

Result of executing a test case against student's code.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class CodingTestCaseResult(models.Model):
    """
    Coding Test Case Result — результат выполнения одного теста.

    Создаётся после async execution в sandbox.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    response = models.ForeignKey(
        'assessment.AssessmentResponse',
        on_delete=models.CASCADE,
        related_name='test_results'
    )

    test_case = models.ForeignKey(
        'assessment.CodingTestCase',
        on_delete=models.PROTECT,
        related_name='results'
    )

    passed = models.BooleanField(
        help_text="TRUE if actual_output matches expected_output"
    )

    actual_output = models.TextField(
        blank=True,
        help_text="stdout from execution"
    )

    execution_time_ms = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Actual execution time"
    )

    memory_used_mb = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Peak memory usage"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error if execution failed (syntax error, runtime error, timeout)"
    )

    points_earned = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Points awarded for this test case"
    )

    class Meta:
        db_table = 'assessment_codingtestcaseresult'
        indexes = [
            models.Index(fields=['response'], name='idx_result_response'),
            models.Index(fields=['test_case'], name='idx_result_testcase'),
        ]

    def __str__(self):
        status = 'PASS' if self.passed else 'FAIL'
        return f"Result for {self.test_case} - {status}"
