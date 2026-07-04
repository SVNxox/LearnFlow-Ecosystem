"""
Assessment Domain Models

Feature-Sliced Architecture (ADR-033):
- One file per model (~100-150 lines)
- Explicit imports, no implicit coupling
"""

from .assessment import ModuleAssessment
from .item import AssessmentItem
from .attempt import AssessmentAttempt
from .response import AssessmentResponse
from .option import AssessmentOption
from .coding import CodingTestCase
from .result import CodingTestCaseResult
from .review import AssessmentReviewLog

__all__ = [
    'ModuleAssessment',
    'AssessmentItem',
    'AssessmentAttempt',
    'AssessmentResponse',
    'AssessmentOption',
    'CodingTestCase',
    'CodingTestCaseResult',
    'AssessmentReviewLog',
]
