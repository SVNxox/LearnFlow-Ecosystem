"""
Assessment Domain Events

Django Signals для внутридоменных событий.
Outbox Pattern для критичных межкомпонентных событий.
"""

from django.dispatch import Signal

attempt_started = Signal()

assessment_passed = Signal()
assessment_failed = Signal()
assessment_needs_review = Signal()

__all__ = [
    'attempt_started',
    'assessment_passed',
    'assessment_failed',
    'assessment_needs_review',
]
