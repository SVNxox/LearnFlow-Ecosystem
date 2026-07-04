"""
Enrollment Domain events (Django Signals).

For non-critical events that don't require guaranteed delivery.
"""

from django.dispatch import Signal



student_enrolled = Signal()  


enrollment_completed = Signal()  


access_granted = Signal()  


access_revoked = Signal()  


enrollment_suspended = Signal()  


enrollment_dropped = Signal()  
