"""
Shared Infrastructure — Outbox Package
"""
from .publisher import publish_to_outbox


def get_outbox_model():
    """Lazy import to avoid circular dependencies."""
    from src.backend.audit.models import DomainEventOutbox
    return DomainEventOutbox

__all__ = [
    'publish_to_outbox',
    'get_outbox_model',
]
