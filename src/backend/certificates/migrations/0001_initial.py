

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text="Template name (e.g., 'Backend Certificate Template')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Template description', null=True)),
                ('background_image', models.TextField(help_text='S3 URL to background image')),
                ('pdf_template', models.TextField(help_text='Path to Jinja2/HTML template for PDF rendering')),
                ('font_config', models.JSONField(default=dict, help_text='Font configuration (family, sizes, colors)')),
                ('layout_config', models.JSONField(default=dict, help_text='Layout configuration (positions, margins, spacing)')),
                ('is_active', models.BooleanField(default=True, help_text='Is this template active?')),
                ('created_by', models.ForeignKey(help_text='User who created this template', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_certificate_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'certificates_template',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enrollment_id', models.UUIDField(help_text='Enrollment ID (soft reference)')),
                ('course_id', models.UUIDField(help_text='Course ID (denormalized)')),
                ('certificate_number', models.CharField(help_text='Unique certificate number (e.g., LF-2026-8AF3D2)', max_length=50, unique=True)),
                ('verification_code', models.CharField(db_index=True, help_text='Public verification code (same as certificate_number)', max_length=50, unique=True)),
                ('student_full_name_snapshot', models.CharField(help_text='Student name at issuance time', max_length=255)),
                ('course_name_snapshot', models.CharField(help_text='Course name at issuance time', max_length=255)),
                ('course_description_snapshot', models.TextField(blank=True, help_text='Course description at issuance time', null=True)),
                ('final_score', models.DecimalField(blank=True, decimal_places=2, help_text='Final course score (percentage)', max_digits=6, null=True)),
                ('completion_date', models.DateField(help_text='Date when course was completed')),
                ('issued_at', models.DateTimeField(help_text='When the certificate was issued')),
                ('pdf_url', models.TextField(blank=True, help_text='S3 URL to generated PDF', null=True)),
                ('pdf_generated_at', models.DateTimeField(blank=True, help_text='When PDF was generated', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('issued', 'Issued'), ('revoked', 'Revoked')], default='pending', help_text='Certificate status', max_length=20)),
                ('revoked_at', models.DateTimeField(blank=True, help_text='When the certificate was revoked', null=True)),
                ('revoked_reason', models.TextField(blank=True, help_text='Reason for revocation', null=True)),
                ('metadata', models.JSONField(default=dict, help_text='Additional metadata')),
                ('revoked_by', models.ForeignKey(blank=True, help_text='Admin who revoked the certificate', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revoked_certificates', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='Student who received the certificate', on_delete=django.db.models.deletion.PROTECT, related_name='certificates', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(help_text='Template used for this certificate', on_delete=django.db.models.deletion.PROTECT, related_name='certificates', to='certificates.certificatetemplate')),
            ],
            options={
                'db_table': 'certificates_certificate',
                'ordering': ['-issued_at'],
            },
        ),
        migrations.CreateModel(
            name='CertificateAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('created', 'Created'), ('issued', 'Issued'), ('revoked', 'Revoked'), ('reissued', 'Reissued'), ('downloaded', 'Downloaded'), ('verified', 'Verified')], help_text='Action performed', max_length=50)),
                ('details', models.JSONField(default=dict, help_text='Additional details about the action')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the actor', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the action was performed')),
                ('actor', models.ForeignKey(blank=True, help_text='User who performed the action', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificate_actions', to=settings.AUTH_USER_MODEL)),
                ('certificate', models.ForeignKey(help_text='Certificate this log belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='audit_logs', to='certificates.certificate')),
            ],
            options={
                'db_table': 'certificates_auditlog',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['certificate', 'created_at'], name='idx_audit_cert'), models.Index(fields=['action', 'created_at'], name='idx_audit_action')],
            },
        ),
        migrations.CreateModel(
            name='CertificateReissueRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason', models.TextField(help_text='Reason for reissue request')),
                ('requested_at', models.DateTimeField(auto_now_add=True, help_text='When the request was made')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', help_text='Request status', max_length=20)),
                ('reviewed_at', models.DateTimeField(blank=True, help_text='When the request was reviewed', null=True)),
                ('certificate', models.ForeignKey(help_text='Original certificate', on_delete=django.db.models.deletion.CASCADE, related_name='reissue_requests', to='certificates.certificate')),
                ('new_certificate', models.OneToOneField(blank=True, help_text='New certificate issued (if approved)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reissued_from_request', to='certificates.certificate')),
                ('requested_by', models.ForeignKey(help_text='User who requested reissue', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificate_reissue_requests', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='Admin who reviewed the request', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_certificate_reissues', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'certificates_reissuerequest',
                'ordering': ['-requested_at'],
                'indexes': [models.Index(fields=['certificate', 'status'], name='idx_reissue_cert_status'), models.Index(fields=['status', 'requested_at'], name='idx_reissue_status')],
                'constraints': [models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'approved', 'rejected'])), name='chk_reissue_status')],
            },
        ),
        migrations.AddIndex(
            model_name='certificatetemplate',
            index=models.Index(fields=['is_active', 'created_at'], name='idx_template_active'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['user', 'status'], name='idx_cert_user_status'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['enrollment_id'], name='idx_cert_enrollment'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['course_id', 'issued_at'], name='idx_cert_course'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['status', 'issued_at'], name='idx_cert_status'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['verification_code'], name='idx_cert_verification'),
        ),
        migrations.AddConstraint(
            model_name='certificate',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'issued', 'revoked'])), name='chk_cert_status'),
        ),
    ]
