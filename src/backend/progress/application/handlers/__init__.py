"""
Application Event Handlers

Handles cross-domain events (integration layer).
"""

from .event_handlers import (
    handle_student_enrolled_outbox,
    handle_submission_approved_outbox,
    PROGRESS_EVENT_HANDLERS,
)

__all__ = [
    'handle_student_enrolled_outbox',
    'handle_submission_approved_outbox',
    'PROGRESS_EVENT_HANDLERS',
]
