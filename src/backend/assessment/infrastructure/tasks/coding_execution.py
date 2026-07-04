"""
Coding Execution Task

Celery task for executing student's code in sandbox.
"""
from decimal import Decimal
from uuid import UUID

from celery import shared_task
from django.db import transaction

from src.backend.assessment.domain.models import (
    AssessmentResponse,
    CodingTestCase,
    CodingTestCaseResult,
)


@shared_task
def execute_coding_task(response_id: str):
    """
    Execute coding response against test cases.

    Steps:
    1. Get response and test cases
    2. Execute code in sandbox (stub for now)
    3. Create CodingTestCaseResult for each test
    4. Calculate auto_points based on passed tests
    5. Update response.auto_points and response.is_graded
    6. Check attempt completion

    Args:
        response_id: UUID of AssessmentResponse
    """
    response = AssessmentResponse.objects.select_related('item').get(id=UUID(response_id))

    
    test_cases = CodingTestCase.objects.filter(item=response.item).order_by('order')

    if not test_cases.exists():
        
        return

    total_points = Decimal('0.00')
    earned_points = Decimal('0.00')

    
    test_cases_with_points = test_cases.exclude(points__isnull=True)
    if test_cases_with_points.exists():
        
        total_points = sum(tc.points for tc in test_cases_with_points)
    else:
        
        total_points = response.item.max_points
        points_per_test = total_points / test_cases.count()

    
    for test_case in test_cases:
        
        
        result = _execute_in_sandbox(
            code=response.submitted_code,
            language=response.coding_language,
            test_input=test_case.input,
            expected_output=test_case.expected_output,
            time_limit_ms=test_case.time_limit_ms,
            memory_limit_mb=test_case.memory_limit_mb,
        )

        
        if test_case.points:
            test_points = test_case.points
        else:
            test_points = points_per_test

        points_earned = test_points if result['passed'] else Decimal('0.00')

        
        CodingTestCaseResult.objects.create(
            response=response,
            test_case=test_case,
            passed=result['passed'],
            actual_output=result['actual_output'],
            execution_time_ms=result['execution_time_ms'],
            memory_used_mb=result['memory_used_mb'],
            error_message=result['error_message'],
            points_earned=points_earned,
        )

        earned_points += points_earned

    
    with transaction.atomic():
        response = AssessmentResponse.objects.select_for_update().get(id=UUID(response_id))
        response.auto_points = earned_points
        response.is_graded = True
        if response.mentor_points is None:
            response.final_points = earned_points
        response.save()

        
        from src.backend.assessment.domain.services import GradingService
        GradingService.check_attempt_completion(response.attempt_id)


def _execute_in_sandbox(
    code: str,
    language: str,
    test_input: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_mb: int,
) -> dict:
    """
    Execute code in sandbox (stub implementation).

    TODO: Integrate with actual sandbox (Docker, Judge0, Piston, etc.)

    Returns:
        dict with keys:
            - passed: bool
            - actual_output: str
            - execution_time_ms: int
            - memory_used_mb: int
            - error_message: str
    """
    
    
    
    
    
    
    
    

    return {
        'passed': False,  
        'actual_output': '[STUB] Sandbox not implemented yet',
        'execution_time_ms': 0,
        'memory_used_mb': 0,
        'error_message': 'Sandbox execution not implemented',
    }
