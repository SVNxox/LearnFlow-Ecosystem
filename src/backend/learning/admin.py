from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Course,
    CourseCategory,
    Lesson,
    LessonContent,
    LessonHomework,
    LessonPractice,
    LessonQuiz,
    Module,
    QuizOption,
    QuizQuestion,
)







class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ("order", "title", "is_published", "estimated_hours")
    ordering = ("order",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order", "title", "is_published", "is_free_preview", "estimated_minutes")
    ordering = ("order",)


class LessonContentInline(admin.TabularInline):
    model = LessonContent
    extra = 0
    fields = ("order", "type", "title", "is_required", "is_downloadable")
    ordering = ("order",)


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    fields = ("order", "type", "body", "points")
    ordering = ("order",)


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 0
    fields = ("order", "body", "is_correct")
    ordering = ("order",)







@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "order", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug")
    ordering = ("parent__name", "order", "name")
    prepopulated_fields = {"slug": ("name",)}







@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "status",
        "category",
        "supports_online",
        "supports_offline",
        "is_sequential",
        "language",
        "created_by",
        "deleted_at",
    )
    list_filter = ("status", "supports_online", "supports_offline", "language", "category")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("created_by", "category")
    inlines = [ModuleInline]

    def get_queryset(self, request):
        
        return Course.all_objects.all()

    def deleted_at(self, obj):
        if obj.deleted_at:
            return format_html(
                '<span style="color: red;">{}</span>', obj.deleted_at.strftime("%Y-%m-%d")
            )
        return "—"

    deleted_at.short_description = "Deleted"







@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_published", "estimated_hours")
    list_filter = ("is_published", "course")
    search_fields = ("title", "course__title")
    raw_id_fields = ("course",)
    inlines = [LessonInline]

    def get_queryset(self, request):
        return Module.all_objects.all()







@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "module",
        "order",
        "is_published",
        "is_free_preview",
        "estimated_minutes",
    )
    list_filter = ("is_published", "is_free_preview")
    search_fields = ("title", "module__title", "module__course__title")
    raw_id_fields = ("module",)
    inlines = [LessonContentInline]

    def get_queryset(self, request):
        return Lesson.all_objects.all()







@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "type", "order", "is_required", "is_downloadable")
    list_filter = ("type", "is_required", "is_downloadable")
    search_fields = ("title", "lesson__title")
    raw_id_fields = ("lesson",)







@admin.register(LessonHomework)
class LessonHomeworkAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "submission_type", "max_score", "deadline_offset_days")
    list_filter = ("submission_type",)
    search_fields = ("title", "lesson__title")
    raw_id_fields = ("lesson",)







@admin.register(LessonPractice)
class LessonPracticeAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "type", "order", "max_score", "time_limit_minutes")
    list_filter = ("type",)
    search_fields = ("title", "lesson__title")
    raw_id_fields = ("lesson",)







@admin.register(LessonQuiz)
class LessonQuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "pass_score",
        "max_attempts",
        "time_limit_minutes",
        "shuffle_questions",
    )
    search_fields = ("title", "lesson__title")
    raw_id_fields = ("lesson",)
    inlines = [QuizQuestionInline]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "quiz", "type", "order", "points")
    list_filter = ("type",)
    search_fields = ("body", "quiz__title")
    raw_id_fields = ("quiz",)
    inlines = [QuizOptionInline]


@admin.register(QuizOption)
class QuizOptionAdmin(admin.ModelAdmin):
    list_display = ("body", "question", "order", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("body",)
    raw_id_fields = ("question",)