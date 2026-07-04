"""
DeliveryFormat value object.
"""

from enum import Enum


class DeliveryFormat(str, Enum):
    """
    How student consumes course content.

    ADR-002: delivery_format lives in CourseEnrollment, not in Course.
    One course can have online and offline students simultaneously.
    """

    ONLINE = 'online'    
    OFFLINE = 'offline'  
    HYBRID = 'hybrid'    

    @property
    def requires_mentor(self) -> bool:
        """Does this format require a mentor?"""
        return self in [DeliveryFormat.OFFLINE, DeliveryFormat.HYBRID]

    @property
    def is_self_paced(self) -> bool:
        """Is this a self-paced format?"""
        return self in [DeliveryFormat.ONLINE, DeliveryFormat.HYBRID]

    @property
    def requires_attendance(self) -> bool:
        """Does this format require attendance tracking?"""
        return self == DeliveryFormat.OFFLINE
