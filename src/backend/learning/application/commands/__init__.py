"""
Learning Domain — Application Layer Commands.

Все write-операции проходят через commands.
Commands применяют бизнес-правила, эмитят события, и выполняются в транзакциях.
"""

from .create_course import CreateCourseCommand, CreateCourseData
from .create_lesson import CreateLessonCommand, CreateLessonData
from .create_module import CreateModuleCommand, CreateModuleData
from .manage_content import ManageContentCommand, AddContentData, UpdateContentData
from .manage_homework import ManageHomeworkCommand, SetHomeworkData
from .manage_practice import ManagePracticeCommand, AddPracticeData, UpdatePracticeData
from .manage_quiz import (
    ManageQuizCommand,
    CreateQuizData,
    UpdateQuizSettingsData,
    AddQuestionData,
    UpdateQuestionData,
    AddOptionData,
)
from .publish_course import PublishCourseCommand
from .update_course import UpdateCourseCommand, UpdateCourseData
from .update_lesson import UpdateLessonCommand, UpdateLessonData
from .update_module import UpdateModuleCommand, UpdateModuleData

__all__ = [
    
    "CreateCourseCommand",
    "PublishCourseCommand",
    "UpdateCourseCommand",
    
    "CreateModuleCommand",
    "UpdateModuleCommand",
    
    "CreateLessonCommand",
    "UpdateLessonCommand",
    
    "ManageContentCommand",
    
    "ManageHomeworkCommand",
    
    "ManagePracticeCommand",
    
    "ManageQuizCommand",
    
    "CreateCourseData",
    "UpdateCourseData",
    "CreateModuleData",
    "UpdateModuleData",
    "CreateLessonData",
    "UpdateLessonData",
    "AddContentData",
    "UpdateContentData",
    "SetHomeworkData",
    "AddPracticeData",
    "UpdatePracticeData",
    "CreateQuizData",
    "UpdateQuizSettingsData",
    "AddQuestionData",
    "UpdateQuestionData",
    "AddOptionData",
]
