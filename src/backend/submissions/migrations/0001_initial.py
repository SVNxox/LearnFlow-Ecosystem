

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lesson_id', models.UUIDField(blank=True, db_index=True, help_text='Soft reference to learning.Lesson (SET NULL)', null=True)),
                ('assessment_item_id', models.UUIDField(blank=True, db_index=True, help_text='Soft reference to assessment.AssessmentItem', null=True)),
                ('type', models.CharField(choices=[('theory', 'Theory'), ('coding', 'Coding Task'), ('project', 'Project')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(help_text='Markdown')),
                ('max_score', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('deadline_offset_days', models.SmallIntegerField(blank=True, help_text='Days from enrollment date', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('submission_types_allowed', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), default=list, help_text="['github_repository', 'file_upload', 'text_answer', 'external_link']")),
                ('allowed_file_extensions', models.CharField(blank=True, help_text='.pdf,.zip,.docx', max_length=200)),
                ('max_file_size_mb', models.SmallIntegerField(default=50, validators=[django.core.validators.MinValueValidator(1)])),
                ('auto_check_enabled', models.BooleanField(default=False, help_text='Enable automatic checks (tests, linting, etc.)')),
                ('auto_check_config', models.JSONField(blank=True, help_text='Configuration for auto-checks', null=True)),
                ('created_by_id', models.UUIDField(db_index=True, help_text='Soft reference to accounts.User (staff)')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'submissions_assignment',
                'indexes': [models.Index(condition=models.Q(('lesson_id__isnull', False)), fields=['lesson_id'], name='idx_assign_lesson'), models.Index(condition=models.Q(('assessment_item_id__isnull', False)), fields=['assessment_item_id'], name='idx_assign_assess'), models.Index(fields=['type'], name='idx_assign_type')],
                'constraints': [models.CheckConstraint(condition=models.Q(('type__in', ['theory', 'coding', 'project'])), name='chk_assign_type_valid'), models.CheckConstraint(condition=models.Q(('lesson_id__isnull', False), ('assessment_item_id__isnull', False), _connector='OR'), name='chk_assign_has_parent')],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True, help_text='Soft reference to enrollment.CourseEnrollment')),
                ('student_id', models.UUIDField(db_index=True, help_text='Denormalized for quick queries')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('under_review', 'Under Review'), ('changes_requested', 'Changes Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], db_index=True, default='draft', max_length=20)),
                ('current_revision_number', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('final_score', models.DecimalField(blank=True, decimal_places=2, help_text='Final score after approval', max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('first_submitted_at', models.DateTimeField(blank=True, help_text='When first submitted for review', null=True)),
                ('last_submitted_at', models.DateTimeField(blank=True, help_text='When last submitted for review', null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, help_text='When approved or rejected', null=True)),
                ('deadline', models.DateTimeField(blank=True, help_text='Calculated from assignment.deadline_offset_days', null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submissions', to='submissions.assignment')),
            ],
            options={
                'db_table': 'submissions_submission',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionRevision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('revision_number', models.SmallIntegerField(help_text='1, 2, 3...', validators=[django.core.validators.MinValueValidator(1)])),
                ('submission_type', models.CharField(choices=[('github_repository', 'GitHub Repository'), ('file_upload', 'File Upload'), ('text_answer', 'Text Answer'), ('external_link', 'External Link')], max_length=20)),
                ('payload', models.JSONField(help_text='Content depends on submission_type')),
                ('notes', models.TextField(blank=True, help_text="Student's notes when submitting")),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='submissions.submission')),
            ],
            options={
                'db_table': 'submissions_submissionrevision',
                'ordering': ['submission', 'revision_number'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True, help_text='Soft reference to accounts.User (mentor)')),
                ('score', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('max_score', models.DecimalField(decimal_places=2, help_text='Snapshot from assignment', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('feedback', models.TextField(help_text="Mentor's feedback")),
                ('status', models.CharField(choices=[('changes_requested', 'Changes Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], max_length=20)),
                ('reviewed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='submissions.submission')),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='submissions.submissionrevision')),
            ],
            options={
                'db_table': 'submissions_submissionreview',
            },
        ),
        migrations.CreateModel(
            name='SubmissionFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_name', models.CharField(max_length=255)),
                ('file_size_bytes', models.BigIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('mime_type', models.CharField(help_text='Validated from file content, not extension', max_length=100)),
                ('storage_path', models.TextField(help_text='S3 path: submissions/{revision_id}/{file_id}')),
                ('scan_status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('passed', 'Passed'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
                ('scan_result', models.JSONField(blank=True, help_text='ClamAV scan results', null=True)),
                ('scanned_at', models.DateTimeField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='submissions.submissionrevision')),
            ],
            options={
                'db_table': 'submissions_submissionfile',
            },
        ),
        migrations.CreateModel(
            name='AutoCheck',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('check_type', models.CharField(help_text='tests, linting, coverage, docker_build, security', max_length=30)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('passed', 'Passed'), ('failed', 'Failed'), ('error', 'Error')], db_index=True, default='pending', max_length=20)),
                ('score', models.DecimalField(blank=True, decimal_places=2, help_text='Score if applicable', max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('report', models.JSONField(help_text='Detailed check results')),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_checks', to='submissions.submissionrevision')),
            ],
            options={
                'db_table': 'submissions_autocheck',
            },
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['enrollment_id', 'assignment'], name='idx_subm_enr_assign'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['student_id', 'status'], name='idx_subm_student_status'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['status'], name='idx_subm_status'),
        ),
        migrations.AddConstraint(
            model_name='submission',
            constraint=models.UniqueConstraint(fields=('enrollment_id', 'assignment'), name='uq_subm_enr_assign'),
        ),
        migrations.AddConstraint(
            model_name='submission',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['draft', 'submitted', 'under_review', 'changes_requested', 'approved', 'rejected'])), name='chk_subm_status_valid'),
        ),
        migrations.AddIndex(
            model_name='submissionrevision',
            index=models.Index(fields=['submission', 'revision_number'], name='idx_rev_subm_num'),
        ),
        migrations.AddConstraint(
            model_name='submissionrevision',
            constraint=models.UniqueConstraint(fields=('submission', 'revision_number'), name='uq_rev_subm_num'),
        ),
        migrations.AddConstraint(
            model_name='submissionrevision',
            constraint=models.CheckConstraint(condition=models.Q(('submission_type__in', ['github_repository', 'file_upload', 'text_answer', 'external_link'])), name='chk_rev_type_valid'),
        ),
        migrations.AddIndex(
            model_name='submissionreview',
            index=models.Index(fields=['submission'], name='idx_review_submission'),
        ),
        migrations.AddIndex(
            model_name='submissionreview',
            index=models.Index(fields=['revision'], name='idx_review_revision'),
        ),
        migrations.AddIndex(
            model_name='submissionreview',
            index=models.Index(fields=['mentor_id'], name='idx_review_mentor'),
        ),
        migrations.AddConstraint(
            model_name='submissionreview',
            constraint=models.UniqueConstraint(fields=('submission', 'revision'), name='uq_review_subm_rev'),
        ),
        migrations.AddConstraint(
            model_name='submissionreview',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['changes_requested', 'approved', 'rejected'])), name='chk_review_status_valid'),
        ),
        migrations.AddConstraint(
            model_name='submissionreview',
            constraint=models.CheckConstraint(condition=models.Q(('score__lte', models.F('max_score'))), name='chk_review_score_valid'),
        ),
        migrations.AddIndex(
            model_name='submissionfile',
            index=models.Index(fields=['revision'], name='idx_file_revision'),
        ),
        migrations.AddIndex(
            model_name='submissionfile',
            index=models.Index(condition=models.Q(('scan_status__in', ['pending', 'running'])), fields=['scan_status', 'uploaded_at'], name='idx_file_scan_pending'),
        ),
        migrations.AddConstraint(
            model_name='submissionfile',
            constraint=models.CheckConstraint(condition=models.Q(('scan_status__in', ['pending', 'running', 'passed', 'failed'])), name='chk_file_scan_valid'),
        ),
        migrations.AddIndex(
            model_name='autocheck',
            index=models.Index(fields=['revision', 'check_type'], name='idx_check_rev_type'),
        ),
        migrations.AddIndex(
            model_name='autocheck',
            index=models.Index(fields=['status'], name='idx_check_status'),
        ),
        migrations.AddConstraint(
            model_name='autocheck',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'running', 'passed', 'failed', 'error'])), name='chk_check_status_valid'),
        ),
    ]
