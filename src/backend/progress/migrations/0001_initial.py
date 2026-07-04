

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True, unique=True)),
                ('course_id', models.UUIDField(db_index=True)),
                ('user_id', models.UUIDField(db_index=True)),
                ('delivery_format', models.CharField(max_length=10)),
                ('is_sequential', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], db_index=True, default='not_started', max_length=20)),
                ('total_modules_count', models.SmallIntegerField(default=0)),
                ('completed_modules_count', models.SmallIntegerField(default=0)),
                ('cached_percentage', models.SmallIntegerField(default=0)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_activity_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Course Progress',
                'verbose_name_plural': 'Course Progress',
                'db_table': 'progress_courseprogress',
                'ordering': ['-last_activity_at'],
                'indexes': [models.Index(fields=['user_id', 'status'], name='idx_cp_user_status'), models.Index(fields=['enrollment_id'], name='idx_cp_enrollment')],
                'constraints': [models.CheckConstraint(condition=models.Q(('completed_modules_count__lte', models.F('total_modules_count'))), name='chk_cprogress_modules_count'), models.CheckConstraint(condition=models.Q(('completed_at__isnull', True), ('status', 'completed'), _connector='OR'), name='chk_cprogress_completed_status')],
            },
        ),
        migrations.CreateModel(
            name='LessonContentView',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True)),
                ('content_id', models.UUIDField()),
                ('lesson_progress_id', models.UUIDField(db_index=True)),
                ('is_required', models.BooleanField()),
                ('first_viewed_at', models.DateTimeField(auto_now_add=True)),
                ('last_viewed_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.SmallIntegerField(default=1)),
                ('last_position_seconds', models.IntegerField(blank=True, null=True)),
                ('total_duration_seconds', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'progress_lessoncontentview',
                'ordering': ['-last_viewed_at'],
                'indexes': [models.Index(fields=['enrollment_id', 'is_required'], name='progress_le_enrollm_7c7c10_idx'), models.Index(fields=['lesson_progress_id'], name='progress_le_lesson__4a6e67_idx')],
                'unique_together': {('enrollment_id', 'content_id')},
            },
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True)),
                ('lesson_id', models.UUIDField(db_index=True)),
                ('module_id', models.UUIDField()),
                ('course_id', models.UUIDField()),
                ('lesson_order', models.SmallIntegerField()),
                ('module_order', models.SmallIntegerField()),
                ('status', models.CharField(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='locked', max_length=20)),
                ('completion_source', models.CharField(blank=True, choices=[('student_activity', 'Student Activity'), ('mentor_attendance', 'Mentor Attendance'), ('mentor_override', 'Mentor Override'), ('admin_override', 'Admin Override')], max_length=30, null=True)),
                ('required_content_count', models.SmallIntegerField(default=0)),
                ('viewed_required_count', models.SmallIntegerField(default=0)),
                ('homework_required', models.BooleanField(default=False)),
                ('homework_submitted', models.BooleanField(default=False)),
                ('homework_submitted_at', models.DateTimeField(blank=True, null=True)),
                ('is_stale', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('override_by_id', models.UUIDField(blank=True, null=True)),
                ('override_reason', models.TextField(blank=True, null=True)),
                ('unlocked_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'progress_lessonprogress',
                'ordering': ['module_order', 'lesson_order'],
                'indexes': [models.Index(condition=models.Q(('is_active', True), ('is_stale', False), ('status__in', ['unlocked', 'in_progress'])), fields=['enrollment_id', 'module_order', 'lesson_order'], name='idx_lp_enr_mod_lesson'), models.Index(fields=['enrollment_id', 'status'], name='progress_le_enrollm_0f9119_idx'), models.Index(fields=['lesson_id'], name='progress_le_lesson__7d0f4b_idx'), models.Index(fields=['module_id'], name='progress_le_module__d8f12f_idx')],
                'constraints': [models.CheckConstraint(condition=models.Q(('viewed_required_count__lte', models.F('required_content_count'))), name='chk_lp_viewed_lte_required'), models.CheckConstraint(condition=models.Q(models.Q(('completed_at__isnull', True), ('status', 'completed'), _connector='OR')), name='chk_lp_completed_at_consistency')],
                'unique_together': {('enrollment_id', 'lesson_id')},
            },
        ),
        migrations.CreateModel(
            name='ModuleProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True)),
                ('module_id', models.UUIDField(db_index=True)),
                ('course_id', models.UUIDField(db_index=True)),
                ('module_order', models.SmallIntegerField()),
                ('status', models.CharField(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked'), ('in_progress', 'In Progress'), ('assessment_pending', 'Assessment Pending'), ('completed', 'Completed')], db_index=True, default='locked', max_length=25)),
                ('total_lessons_count', models.SmallIntegerField(default=0)),
                ('completed_lessons_count', models.SmallIntegerField(default=0)),
                ('assessment_required', models.BooleanField(default=False)),
                ('assessment_passed', models.BooleanField(default=False)),
                ('assessment_passed_at', models.DateTimeField(blank=True, null=True)),
                ('is_stale', models.BooleanField(db_index=True, default=False)),
                ('unlocked_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_activity_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Module Progress',
                'verbose_name_plural': 'Module Progress',
                'db_table': 'progress_moduleprogress',
                'ordering': ['enrollment_id', 'module_order'],
                'indexes': [models.Index(fields=['enrollment_id', 'module_order'], name='idx_mp_enr_order'), models.Index(fields=['enrollment_id', 'status'], name='idx_mp_enr_status')],
                'constraints': [models.UniqueConstraint(fields=('enrollment_id', 'module_id'), name='uq_moduleprogress_enr_module'), models.CheckConstraint(condition=models.Q(('completed_lessons_count__lte', models.F('total_lessons_count'))), name='chk_mprogress_lessons_count'), models.CheckConstraint(condition=models.Q(('completed_at__isnull', True), ('status', 'completed'), _connector='OR'), name='chk_mprogress_completed_status')],
            },
        ),
    ]
