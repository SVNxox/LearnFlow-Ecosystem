

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
            name='AssessmentAttempt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True, help_text='Soft reference to enrollment.CourseEnrollment')),
                ('user_id', models.UUIDField(db_index=True, help_text='Denormalized from enrollment for quick queries')),
                ('attempt_number', models.SmallIntegerField(help_text='1, 2, 3... (per enrollment)', validators=[django.core.validators.MinValueValidator(1)])),
                ('grading_status', models.CharField(choices=[('pending', 'Pending'), ('auto_graded', 'Auto-Graded'), ('mentor_review', 'Awaiting Mentor Review'), ('finalized', 'Finalized')], db_index=True, default='pending', max_length=20)),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submitted_at', models.DateTimeField(blank=True, help_text='When student submitted all responses', null=True)),
                ('graded_at', models.DateTimeField(blank=True, help_text='When grading_status became finalized', null=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Set if time_limit_minutes configured', null=True)),
                ('max_score', models.DecimalField(decimal_places=2, help_text='Snapshot of assessment.max_score', max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('final_score', models.DecimalField(blank=True, decimal_places=2, help_text='Sum of final_points from all responses', max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, help_text='final_score / max_score * 100', max_digits=5, null=True)),
                ('passed', models.BooleanField(blank=True, help_text='percentage >= passing_percentage', null=True)),
                ('mentor_note', models.TextField(blank=True, help_text='General comment from mentor')),
            ],
            options={
                'db_table': 'assessment_assessmentattempt',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='AssessmentItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('single_choice', 'Single Choice'), ('multiple_choice', 'Multiple Choice'), ('text_answer', 'Text Answer'), ('coding', 'Coding Task'), ('project', 'Project Task'), ('interview', 'Interview Question')], max_length=20)),
                ('order', models.SmallIntegerField(help_text='Display order (1, 2, 3...)', validators=[django.core.validators.MinValueValidator(1)])),
                ('title', models.TextField(help_text='Question text or task description')),
                ('description', models.TextField(blank=True, help_text='Additional context or instructions')),
                ('max_points', models.DecimalField(decimal_places=2, help_text='Maximum points for this item', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('partial_credit_strategy', models.CharField(choices=[('all_or_nothing', 'All or Nothing'), ('proportional', 'Proportional')], default='all_or_nothing', help_text='How to award partial credit (for multiple_choice and coding)', max_length=20)),
                ('explanation', models.TextField(blank=True, help_text='Shown after grading (why answer is correct/wrong)')),
                ('mentor_review_required', models.BooleanField(default=False, help_text='TRUE for text_answer, project, interview')),
                ('coding_language', models.CharField(blank=True, help_text='python, javascript, java, etc.', max_length=30)),
                ('starter_code', models.TextField(blank=True, help_text='Pre-filled code template')),
                ('sample_answer', models.TextField(blank=True, help_text='Reference answer for mentor (text_answer type)')),
                ('min_word_count', models.SmallIntegerField(blank=True, help_text='Minimum words required (text_answer)', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('submission_requirements', models.TextField(blank=True, help_text='Project requirements checklist')),
            ],
            options={
                'db_table': 'assessment_assessmentitem',
                'ordering': ['assessment', 'order'],
            },
        ),
        migrations.CreateModel(
            name='AssessmentResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('selected_option_ids', django.contrib.postgres.fields.ArrayField(base_field=models.UUIDField(), blank=True, default=list, help_text='For single_choice and multiple_choice')),
                ('text_response', models.TextField(blank=True, help_text='For text_answer and interview')),
                ('submitted_code', models.TextField(blank=True, help_text='For coding type')),
                ('coding_language', models.CharField(blank=True, help_text='Language used for coding submission', max_length=30)),
                ('submission_id', models.UUIDField(blank=True, help_text='Soft reference to submissions.ProjectSubmission (for project type)', null=True)),
                ('is_graded', models.BooleanField(db_index=True, default=False)),
                ('auto_points', models.DecimalField(blank=True, decimal_places=2, help_text='Auto-grading result', max_digits=6, null=True)),
                ('mentor_points', models.DecimalField(blank=True, decimal_places=2, help_text='Mentor override (takes precedence)', max_digits=6, null=True)),
                ('final_points', models.DecimalField(blank=True, decimal_places=2, help_text='COALESCE(mentor_points, auto_points)', max_digits=6, null=True)),
                ('is_correct', models.BooleanField(blank=True, help_text='For choice items (binary correct/incorrect)', null=True)),
                ('reviewed_by_id', models.UUIDField(blank=True, db_index=True, help_text='Soft reference to accounts.User (mentor)', null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_comment', models.TextField(blank=True, help_text="Mentor's feedback or reason for override")),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='assessment.assessmentattempt')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='responses', to='assessment.assessmentitem')),
            ],
            options={
                'db_table': 'assessment_assessmentresponse',
            },
        ),
        migrations.CreateModel(
            name='AssessmentReviewLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attempt_id', models.UUIDField(db_index=True, help_text='Denormalized for quick queries')),
                ('old_score', models.DecimalField(decimal_places=2, help_text='Score before change', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('new_score', models.DecimalField(decimal_places=2, help_text='Score after change', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('mentor_id', models.UUIDField(db_index=True, help_text='Soft reference to accounts.User (mentor)')),
                ('reason', models.TextField(help_text='Why the score was changed (required)')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_logs', to='assessment.assessmentresponse')),
            ],
            options={
                'db_table': 'assessment_assessmentreviewlog',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CodingTestCase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('input', models.TextField(help_text='stdin input or function arguments')),
                ('expected_output', models.TextField(help_text='Expected output (compared with actual)')),
                ('points', models.DecimalField(blank=True, decimal_places=2, help_text='Points for this test case (NULL = equal distribution)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('time_limit_ms', models.IntegerField(default=2000, help_text='Execution time limit in milliseconds', validators=[django.core.validators.MinValueValidator(100)])),
                ('memory_limit_mb', models.IntegerField(default=128, help_text='Memory limit in megabytes', validators=[django.core.validators.MinValueValidator(16)])),
                ('is_hidden', models.BooleanField(default=False, help_text='Hidden test cases are not shown to student')),
                ('is_sample', models.BooleanField(default=False, help_text='Sample test cases shown in problem description')),
                ('order', models.SmallIntegerField(help_text='Execution order', validators=[django.core.validators.MinValueValidator(1)])),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_cases', to='assessment.assessmentitem')),
            ],
            options={
                'db_table': 'assessment_codingtestcase',
                'ordering': ['item', 'order'],
            },
        ),
        migrations.CreateModel(
            name='CodingTestCaseResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('passed', models.BooleanField(help_text='TRUE if actual_output matches expected_output')),
                ('actual_output', models.TextField(blank=True, help_text='stdout from execution')),
                ('execution_time_ms', models.IntegerField(blank=True, help_text='Actual execution time', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('memory_used_mb', models.IntegerField(blank=True, help_text='Peak memory usage', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('error_message', models.TextField(blank=True, help_text='Error if execution failed (syntax error, runtime error, timeout)')),
                ('points_earned', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Points awarded for this test case', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='assessment.assessmentresponse')),
                ('test_case', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='results', to='assessment.codingtestcase')),
            ],
            options={
                'db_table': 'assessment_codingtestcaseresult',
            },
        ),
        migrations.CreateModel(
            name='ModuleAssessment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('module_id', models.UUIDField(db_index=True, help_text='Soft reference to learning.Module', unique=True)),
                ('title', models.CharField(max_length=255)),
                ('instructions', models.TextField(blank=True, help_text='Instructions shown to student before starting')),
                ('passing_percentage', models.DecimalField(decimal_places=2, default=Decimal('70.00'), help_text='Percentage required to pass (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))])),
                ('max_attempts', models.SmallIntegerField(blank=True, help_text='NULL = unlimited attempts', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('time_limit_minutes', models.SmallIntegerField(blank=True, help_text='NULL = no time limit', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('shuffle_items', models.BooleanField(default=False, help_text='Randomize item order for each attempt')),
                ('is_published', models.BooleanField(default=False, help_text='Only published assessments are visible to students')),
                ('created_by_id', models.UUIDField(db_index=True, help_text='Soft reference to accounts.User (staff)')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'assessment_moduleassessment',
                'ordering': ['created_at'],
                'indexes': [models.Index(fields=['module_id'], name='idx_assess_module'), models.Index(fields=['is_published'], name='idx_assess_published'), models.Index(fields=['created_by_id'], name='idx_assess_creator')],
            },
        ),
        migrations.AddField(
            model_name='assessmentitem',
            name='assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='assessment.moduleassessment'),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attempts', to='assessment.moduleassessment'),
        ),
        migrations.CreateModel(
            name='AssessmentOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField(help_text='Option text')),
                ('is_correct', models.BooleanField(default=False, help_text='TRUE if this is a correct answer')),
                ('order', models.SmallIntegerField(help_text='Display order', validators=[django.core.validators.MinValueValidator(1)])),
                ('explanation', models.TextField(blank=True, help_text='Shown after grading (why this option is correct/incorrect)')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='assessment.assessmentitem')),
            ],
            options={
                'db_table': 'assessment_assessmentoption',
                'ordering': ['item', 'order'],
                'indexes': [models.Index(fields=['item', 'order'], name='idx_opt_item_order')],
                'constraints': [models.UniqueConstraint(fields=('item', 'order'), name='uq_opt_item_order')],
            },
        ),
        migrations.AddIndex(
            model_name='assessmentresponse',
            index=models.Index(fields=['attempt', 'item'], name='idx_resp_attempt_item'),
        ),
        migrations.AddIndex(
            model_name='assessmentresponse',
            index=models.Index(fields=['is_graded'], name='idx_resp_graded'),
        ),
        migrations.AddIndex(
            model_name='assessmentresponse',
            index=models.Index(fields=['reviewed_by_id'], name='idx_resp_reviewer'),
        ),
        migrations.AddConstraint(
            model_name='assessmentresponse',
            constraint=models.UniqueConstraint(fields=('attempt', 'item'), name='uq_resp_attempt_item'),
        ),
        migrations.AddIndex(
            model_name='assessmentreviewlog',
            index=models.Index(fields=['response'], name='idx_revlog_response'),
        ),
        migrations.AddIndex(
            model_name='assessmentreviewlog',
            index=models.Index(fields=['attempt_id'], name='idx_revlog_attempt'),
        ),
        migrations.AddIndex(
            model_name='assessmentreviewlog',
            index=models.Index(fields=['mentor_id'], name='idx_revlog_mentor'),
        ),
        migrations.AddIndex(
            model_name='assessmentreviewlog',
            index=models.Index(fields=['-created_at'], name='idx_revlog_created'),
        ),
        migrations.AddIndex(
            model_name='codingtestcase',
            index=models.Index(fields=['item', 'order'], name='idx_testcase_item_order'),
        ),
        migrations.AddIndex(
            model_name='codingtestcase',
            index=models.Index(fields=['is_sample'], name='idx_testcase_sample'),
        ),
        migrations.AddIndex(
            model_name='codingtestcaseresult',
            index=models.Index(fields=['response'], name='idx_result_response'),
        ),
        migrations.AddIndex(
            model_name='codingtestcaseresult',
            index=models.Index(fields=['test_case'], name='idx_result_testcase'),
        ),
        migrations.AddIndex(
            model_name='assessmentitem',
            index=models.Index(fields=['assessment', 'order'], name='idx_item_assess_order'),
        ),
        migrations.AddIndex(
            model_name='assessmentitem',
            index=models.Index(fields=['type'], name='idx_item_type'),
        ),
        migrations.AddConstraint(
            model_name='assessmentitem',
            constraint=models.UniqueConstraint(fields=('assessment', 'order'), name='uq_item_assess_order'),
        ),
        migrations.AddIndex(
            model_name='assessmentattempt',
            index=models.Index(fields=['enrollment_id', 'assessment'], name='idx_attempt_enr_assess'),
        ),
        migrations.AddIndex(
            model_name='assessmentattempt',
            index=models.Index(fields=['user_id', 'grading_status'], name='idx_attempt_user_status'),
        ),
        migrations.AddIndex(
            model_name='assessmentattempt',
            index=models.Index(fields=['grading_status'], name='idx_attempt_status'),
        ),
        migrations.AddConstraint(
            model_name='assessmentattempt',
            constraint=models.UniqueConstraint(fields=('enrollment_id', 'assessment', 'attempt_number'), name='uq_attempt_enr_assess_num'),
        ),
        migrations.AddConstraint(
            model_name='assessmentattempt',
            constraint=models.CheckConstraint(condition=models.Q(('final_score__lte', models.F('max_score'))), name='chk_attempt_score_valid'),
        ),
    ]
