"""
Certificate Template model
"""

import uuid

from django.db import models
from django.conf import settings


class CertificateTemplate(models.Model):
    """
    Certificate template for PDF generation.

    Different courses can use different templates (design, layout, colors).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=255,
        help_text="Template name (e.g., 'Backend Certificate Template')"
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Template description"
    )

    background_image = models.TextField(
        help_text="S3 URL to background image"
    )

    pdf_template = models.TextField(
        help_text="Path to Jinja2/HTML template for PDF rendering"
    )

    font_config = models.JSONField(
        default=dict,
        help_text="Font configuration (family, sizes, colors)"
    )

    layout_config = models.JSONField(
        default=dict,
        help_text="Layout configuration (positions, margins, spacing)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this template active?"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_certificate_templates',
        help_text="User who created this template"
    )

    class Meta:
        db_table = 'certificates_template'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'created_at'], name='idx_template_active'),
        ]

    def __str__(self):
        return self.name
