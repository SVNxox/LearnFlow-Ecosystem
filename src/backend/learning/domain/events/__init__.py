"""
Learning Domain — Domain Events.

События эмитятся после успешного commit транзакции.
Используются для cross-domain communication и audit trail.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CourseCreated:
    """Курс создан."""

    event_type: str = "CourseCreated"
    course_id: str = ""
    title: str = ""
    slug: str = ""
    created_by_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, course_id: str, title: str, slug: str, created_by_id: str):
        self.event_type = "CourseCreated"
        self.course_id = course_id
        self.title = title
        self.slug = slug
        self.created_by_id = created_by_id
        self.timestamp = datetime.utcnow()


@dataclass
class CoursePublished:
    """
    Курс опубликован.

    Consumers:
    - Enrollment Domain: начать принимать enrollments
    - Analytics: track publication event
    - Notifications: уведомить подписчиков
    """

    event_type: str = "CoursePublished"
    course_id: str = ""
    title: str = ""
    slug: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, course_id: str, title: str, slug: str, actor_id: str):
        self.event_type = "CoursePublished"
        self.course_id = course_id
        self.title = title
        self.slug = slug
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class CourseUnpublished:
    """Курс снят с публикации."""

    event_type: str = "CourseUnpublished"
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, course_id: str, actor_id: str):
        self.event_type = "CourseUnpublished"
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class CourseArchived:
    """Курс архивирован."""

    event_type: str = "CourseArchived"
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, course_id: str, actor_id: str):
        self.event_type = "CourseArchived"
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class CourseDeleted:
    """Курс soft-deleted."""

    event_type: str = "CourseDeleted"
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, course_id: str, actor_id: str):
        self.event_type = "CourseDeleted"
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class ModuleCreated:
    """Модуль создан."""

    event_type: str = "ModuleCreated"
    module_id: str = ""
    course_id: str = ""
    title: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, module_id: str, course_id: str, title: str, actor_id: str):
        self.event_type = "ModuleCreated"
        self.module_id = module_id
        self.course_id = course_id
        self.title = title
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class ModulePublished:
    """Модуль опубликован."""

    event_type: str = "ModulePublished"
    module_id: str = ""
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, module_id: str, course_id: str, actor_id: str):
        self.event_type = "ModulePublished"
        self.module_id = module_id
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class LessonCreated:
    """Урок создан."""

    event_type: str = "LessonCreated"
    lesson_id: str = ""
    module_id: str = ""
    course_id: str = ""
    title: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(
        self, lesson_id: str, module_id: str, course_id: str, title: str, actor_id: str
    ):
        self.event_type = "LessonCreated"
        self.lesson_id = lesson_id
        self.module_id = module_id
        self.course_id = course_id
        self.title = title
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class LessonPublished:
    """
    Урок опубликован.

    Consumers:
    - UserProgress Domain: unlock lesson для enrolled студентов (fan-out async)
    """

    event_type: str = "LessonPublished"
    lesson_id: str = ""
    module_id: str = ""
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, lesson_id: str, module_id: str, course_id: str, actor_id: str):
        self.event_type = "LessonPublished"
        self.lesson_id = lesson_id
        self.module_id = module_id
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class LessonDeleted:
    """
    Урок soft-deleted.

    Consumers:
    - UserProgress Domain: mark progress records as orphaned (fan-out async)
    - Submissions Domain: mark submissions as orphaned
    """

    event_type: str = "LessonDeleted"
    lesson_id: str = ""
    module_id: str = ""
    course_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, lesson_id: str, module_id: str, course_id: str, actor_id: str):
        self.event_type = "LessonDeleted"
        self.lesson_id = lesson_id
        self.module_id = module_id
        self.course_id = course_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


@dataclass
class ContentDeleted:
    """
    Контент элемент удалён.

    Consumers:
    - UserProgress Domain: remove ContentView records (fan-out async)
    """

    event_type: str = "ContentDeleted"
    content_id: str = ""
    lesson_id: str = ""
    actor_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, content_id: str, lesson_id: str, actor_id: str):
        self.event_type = "ContentDeleted"
        self.content_id = content_id
        self.lesson_id = lesson_id
        self.actor_id = actor_id
        self.timestamp = datetime.utcnow()


__all__ = [
    "CourseCreated",
    "CoursePublished",
    "CourseUnpublished",
    "CourseArchived",
    "CourseDeleted",
    "ModuleCreated",
    "ModulePublished",
    "LessonCreated",
    "LessonPublished",
    "LessonDeleted",
    "ContentDeleted",
]
