"""
AccessLevel value object.
"""

from enum import Enum


class AccessLevel(str, Enum):
    """
    Level of access student has to course content.

    Used for:
    - Free trials (PREVIEW)
    - Partial access (LIMITED)
    - Full paid access (FULL)
    """

    FULL = 'full'           
    LIMITED = 'limited'     
    PREVIEW = 'preview'     

    @property
    def can_track_progress(self) -> bool:
        """Can we track progress for this access level?"""
        return self in [AccessLevel.FULL, AccessLevel.LIMITED]

    @property
    def can_earn_certificate(self) -> bool:
        """Can student earn certificate with this access?"""
        return self == AccessLevel.FULL

    @property
    def is_paid(self) -> bool:
        """Does this access level require payment?"""
        return self == AccessLevel.FULL
