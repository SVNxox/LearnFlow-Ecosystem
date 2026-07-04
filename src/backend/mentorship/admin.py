"""
Django Admin configuration for Mentorship Domain
"""

from django.contrib import admin
from django.utils.html import format_html

from src.backend.mentorship.domain.models.mentor_group import MentorGroup
from src.backend.mentorship.domain.models.student_group import StudentMentorGroup
from src.backend.mentorship.domain.models.offline_session import OfflineSession
from src.backend.mentorship.domain.models.attendance import Attendance


class StudentMentorGroupInline(admin.TabularInline):
    """Inline for StudentMentorGroup."""
    model = StudentMentorGroup
    extra = 0
    readonly_fields = ['student_id', 'enrollment_id', 'joined_at', 'left_at']
    fields = ['student_id', 'enrollment_id', 'joined_at', 'left_at']


class OfflineSessionInline(admin.TabularInline):
    """Inline for OfflineSession."""
    model = OfflineSession
    extra = 0
    readonly_fields = ['scheduled_start', 'scheduled_end', 'status']
    fields = ['scheduled_start', 'scheduled_end', 'lesson_id', 'status']


@admin.register(MentorGroup)
class MentorGroupAdmin(admin.ModelAdmin):
    """Admin for MentorGroup."""

    list_display = [
        'name',
        'mentor_link',
        'max_students',
        'created_at',
    ]

    list_filter = [
        'created_at',
    ]

    search_fields = [
        'name',
        'mentor_id',
        'course_id',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Group Info', {
            'fields': ('name', 'mentor', 'course_id')
        }),
        ('Capacity', {
            'fields': ('max_students', 'planned_lessons_count')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )

    inlines = [StudentMentorGroupInline, OfflineSessionInline]

    def mentor_link(self, obj):
        return str(obj.mentor_id)[:8]
    mentor_link.short_description = 'Mentor'


@admin.register(StudentMentorGroup)
class StudentMentorGroupAdmin(admin.ModelAdmin):
    """Admin for StudentMentorGroup."""

    list_display = [
        'id_short',
        'group_link',
        'student_id_short',
        'enrollment_id_short',
        'joined_at',
        'is_active',
    ]

    list_filter = [
        'joined_at',
        'left_at',
    ]

    search_fields = [
        'group_id',
        'student_id',
        'enrollment_id',
    ]

    readonly_fields = [
        'id',
        'group_id',
        'student_id',
        'enrollment_id',
        'joined_at',
        'left_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'group_id', 'student_id', 'enrollment_id')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'left_at')
        }),
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def group_link(self, obj):
        return format_html(
            '<a href="/admin/mentorship/mentorgroup/{}/change/">{}</a>',
            obj.group_id,
            obj.group.name if obj.group else str(obj.group_id)[:8]
        )
    group_link.short_description = 'Group'

    def student_id_short(self, obj):
        return str(obj.student_id)[:8]
    student_id_short.short_description = 'Student'

    def enrollment_id_short(self, obj):
        return str(obj.enrollment_id)[:8]
    enrollment_id_short.short_description = 'Enrollment'

    def is_active(self, obj):
        return obj.left_at is None
    is_active.boolean = True
    is_active.short_description = 'Active'


class AttendanceInline(admin.TabularInline):
    """Inline for Attendance."""
    model = Attendance
    extra = 0
    readonly_fields = ['student_id', 'status', 'marked_by_id', 'marked_at']
    fields = ['student_id', 'status', 'marked_by_id', 'marked_at', 'notes']


@admin.register(OfflineSession)
class OfflineSessionAdmin(admin.ModelAdmin):
    """Admin for OfflineSession."""

    list_display = [
        'id_short',
        'group_link',
        'lesson_id_short',
        'scheduled_start',
        'status_badge',
        'attendance_count',
    ]

    list_filter = [
        'status',
        'scheduled_start',
    ]

    search_fields = [
        'group_id',
        'lesson_id',
    ]

    readonly_fields = [
        'id',
        'group_id',
        'lesson_id',
        'actual_start',
        'actual_end',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'group_id', 'lesson_id')
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    inlines = [AttendanceInline]

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def group_link(self, obj):
        return format_html(
            '<a href="/admin/mentorship/mentorgroup/{}/change/">{}</a>',
            obj.group_id,
            obj.group.name if obj.group else str(obj.group_id)[:8]
        )
    group_link.short_description = 'Group'

    def lesson_id_short(self, obj):
        return str(obj.lesson_id)[:8] if obj.lesson_id else '-'
    lesson_id_short.short_description = 'Lesson'

    def status_badge(self, obj):
        colors = {
            'scheduled': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'canceled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def attendance_count(self, obj):
        return obj.attendances.count()
    attendance_count.short_description = 'Attendances'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin for Attendance."""

    list_display = [
        'id_short',
        'session_link',
        'student_id_short',
        'status_badge',
        'marked_by_id_short',
        'marked_at',
    ]

    list_filter = [
        'status',
        'marked_at',
    ]

    search_fields = [
        'session_id',
        'student_id',
        'marked_by_id',
    ]

    readonly_fields = [
        'id',
        'session_id',
        'student_id',
        'status',
        'marked_by_id',
        'marked_at',
        'notes',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session_id', 'student_id')
        }),
        ('Attendance', {
            'fields': ('status', 'marked_by_id', 'marked_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def session_link(self, obj):
        return format_html(
            '<a href="/admin/mentorship/offlinesession/{}/change/">{}</a>',
            obj.session_id,
            str(obj.session_id)[:8]
        )
    session_link.short_description = 'Session'

    def student_id_short(self, obj):
        return str(obj.student_id)[:8]
    student_id_short.short_description = 'Student'

    def marked_by_id_short(self, obj):
        return str(obj.marked_by_id)[:8] if obj.marked_by_id else '-'
    marked_by_id_short.short_description = 'Marked By'

    def status_badge(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
