"""
Submissions Domain — Assessment Event Handlers

Handles incoming events from Assessment Domain.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.backend.submissions.application.commands.create_assignment import (
    CreateAssignmentCommand,
)





def handle_assessment_attempt_started(
    sender, attempt_id, student_id, assessment_id, module_id, **kwargs
):
    """
    Создает Assignment при начале attempt с coding items.

    Триггер: assessment.events.assessment_attempt_started

    Бизнес-правило:
    - Если в assessment есть хотя бы один coding item → create Assignment
    - Assignment создается только один раз для attempt_id (идемпотентность)
    """
    from src.backend.submissions.domain.models.assignment import Assignment
    from src.backend.assessment.domain.models.item import AssessmentItem

    
    if Assignment.objects.filter(attempt_id=attempt_id).exists():
        return

    
    has_coding = AssessmentItem.objects.filter(
        assessment_id=assessment_id,
        item_type='coding'
    ).exists()

    if not has_coding:
        return  

    
    from src.backend.assessment.domain.models.assessment import ModuleAssessment
    assessment = ModuleAssessment.objects.get(id=assessment_id)

    
    coding_items = list(
        AssessmentItem.objects.filter(
            assessment_id=assessment_id,
            item_type='coding'
        ).select_related('coding_config')
    )

    task_list = [
        {
            'item_id': str(item.id),
            'title': item.question_text[:100],
            'points': float(item.points),
            'starter_code': item.coding_config.starter_code if item.coding_config else None,
        }
        for item in coding_items
    ]

    
    command = CreateAssignmentCommand(
        attempt_id=attempt_id,
        student_id=student_id,
        module_id=module_id,
        assignment_type='coding_assessment',
        title=f"Coding Tasks: {assessment.title}",
        description=f"Complete all coding tasks from {assessment.title}",
        task_list=task_list,
        max_points=sum(item.points for item in coding_items),
        auto_check_enabled=True,
        max_attempts=assessment.max_attempts or 3,  
        due_date=None,  
    )

    command.execute()

    
    






