"""
Django Admin configuration for Certificates Domain
"""

from django.contrib import admin
from django.utils.html import format_html

from src.backend.certificates.domain.models.certificate import Certificate
from src.backend.certificates.domain.models.template import CertificateTemplate


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    """Admin for CertificateTemplate."""

    list_display = [
        'name',
        'created_at',
    ]

    list_filter = [
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'description')
        }),
        ('Design', {
            'fields': ('pdf_template', 'background_image')
        }),
        ('Configuration', {
            'fields': ('font_config', 'layout_config'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin for Certificate."""

    list_display = [
        'certificate_number',
        'student_name',
        'course_name_short',
        'status_badge',
        'issued_at',
        'verification_link',
    ]

    list_filter = [
        'status',
        'issued_at',
        'revoked_at',
    ]

    search_fields = [
        'certificate_number',
        'verification_code',
        'user_id',
        'enrollment_id',
        'student_full_name_snapshot',
        'course_name_snapshot',
    ]

    readonly_fields = [
        'id',
        'user_id',
        'enrollment_id',
        'course_id',
        'template',
        'certificate_number',
        'verification_code',
        'student_full_name_snapshot',
        'course_name_snapshot',
        'course_description_snapshot',
        'final_score',
        'completion_date',
        'issued_at',
        'pdf_url',
        'pdf_generated_at',
        'revoked_at',
        'revoked_by_id',
        'revoked_reason',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'certificate_number', 'verification_code')
        }),
        ('References', {
            'fields': ('user_id', 'enrollment_id', 'course_id', 'template')
        }),
        ('Snapshot Data', {
            'fields': (
                'student_full_name_snapshot',
                'course_name_snapshot',
                'course_description_snapshot',
                'final_score',
                'completion_date',
            )
        }),
        ('Status', {
            'fields': ('status', 'issued_at', 'pdf_url', 'pdf_generated_at')
        }),
        ('Revocation', {
            'fields': ('revoked_at', 'revoked_by_id', 'revoked_reason'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def student_name(self, obj):
        return obj.student_full_name_snapshot
    student_name.short_description = 'Student'

    def course_name_short(self, obj):
        name = obj.course_name_snapshot
        return name[:50] + '...' if len(name) > 50 else name
    course_name_short.short_description = 'Course'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'issued': 'green',
            'revoked': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def verification_link(self, obj):
        if obj.verification_code:
            return format_html(
                '<a href="/api/v1/certificates/verify/{}/" target="_blank">Verify</a>',
                obj.verification_code
            )
        return '-'
    verification_link.short_description = 'Verify'

    def has_delete_permission(self, request, obj=None):
        
        return False

    def has_add_permission(self, request):
        
        return False
