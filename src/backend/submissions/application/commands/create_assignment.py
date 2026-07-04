"""
Create Assignment Command

Staff creates a new assignment (homework/coding/project).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.db import transaction

from src.backend.submissions.domain.models import Assignment


@dataclass
class CreateAssignmentCommand:
    """
    Create new assignment.

    Called by: Staff when creating lesson content
    """
    lesson_id: Optional[UUID]
    assessment_item_id: Optional[UUID]
    type: str  
    title: str
    description: str
    max_score: Decimal
    deadline_offset_days: Optional[int]
    submission_types_allowed: list[str]
    allowed_file_extensions: Optional[str]
    max_file_size_mb: int
    auto_check_enabled: bool
    auto_check_config: Optional[dict]
    created_by_id: UUID


class CreateAssignmentHandler:
    """
    Handler for CreateAssignmentCommand.

    Validation:
    - lesson_id OR assessment_item_id must be provided (not both)
    - type must be valid (theory/coding/project)
    - submission_types_allowed must not be empty
    """

    @staticmethod
    @transaction.atomic
    def handle(command: CreateAssignmentCommand) -> Assignment:
        
        if not command.lesson_id and not command.assessment_item_id:
            raise ValueError("Either lesson_id or assessment_item_id must be provided")

        if command.lesson_id and command.assessment_item_id:
            raise ValueError("Cannot provide both lesson_id and assessment_item_id")

        if command.type not in ['theory', 'coding', 'project']:
            raise ValueError(f"Invalid type: {command.type}")

        if not command.submission_types_allowed:
            raise ValueError("submission_types_allowed cannot be empty")

        
        assignment = Assignment.objects.create(
            lesson_id=command.lesson_id,
            assessment_item_id=command.assessment_item_id,
            type=command.type,
            title=command.title,
            description=command.description,
            max_score=command.max_score,
            deadline_offset_days=command.deadline_offset_days,
            submission_types_allowed=command.submission_types_allowed,
            allowed_file_extensions=command.allowed_file_extensions,
            max_file_size_mb=command.max_file_size_mb,
            auto_check_enabled=command.auto_check_enabled,
            auto_check_config=command.auto_check_config or {},
            created_by_id=command.created_by_id
        )

        return assignment
