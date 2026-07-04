"""
Learning Domain — Application Layer Queries.

Все read-операции проходят через queries.
Queries применяют visibility rules и оптимизируют запросы.
"""

from .course_catalog import CourseCatalogQuery, CourseCardDTO, CategoryDTO
from .course_detail import CourseDetailQuery, CourseDetailDTO, ModuleDTO, LessonMetadataDTO
from .lesson_detail import (
    LessonDetailQuery,
    LessonDetailDTO,
    ContentItemDTO,
    HomeworkDTO,
    PracticeItemDTO,
    QuizDTO,
    QuizQuestionDTO,
)

__all__ = [
    
    "CourseCatalogQuery",
    "CourseDetailQuery",
    "LessonDetailQuery",
    
    "CourseCardDTO",
    "CategoryDTO",
    "CourseDetailDTO",
    "ModuleDTO",
    "LessonMetadataDTO",
    "LessonDetailDTO",
    "ContentItemDTO",
    "HomeworkDTO",
    "PracticeItemDTO",
    "QuizDTO",
    "QuizQuestionDTO",
]
