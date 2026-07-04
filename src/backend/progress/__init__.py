"""
UserProgress Domain

Tracks student progress through courses, modules, and lessons.
Handles completion cascade (lesson → module → course).

Bounded Context: User learning progress and completion state.
"""

default_app_config = 'src.backend.progress.apps.ProgressConfig'
