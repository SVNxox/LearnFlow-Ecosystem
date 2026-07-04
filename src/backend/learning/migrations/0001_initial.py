

import django.contrib.postgres.fields
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
            name='Lesson',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.SmallIntegerField()),
                ('is_published', models.BooleanField(default=False)),
                ('is_free_preview', models.BooleanField(default=False, help_text='If true, lesson content is visible without enrollment (marketing).')),
                ('estimated_minutes', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Lesson',
                'verbose_name_plural': 'Lessons',
                'db_table': 'courses_lesson',
            },
        ),
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('order', models.SmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='learning.coursecategory')),
            ],
            options={
                'verbose_name': 'Course Category',
                'verbose_name_plural': 'Course Categories',
                'db_table': 'courses_coursecategory',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('short_description', models.CharField(blank=True, max_length=500, null=True)),
                ('thumbnail_url', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('supports_online', models.BooleanField(default=True)),
                ('supports_offline', models.BooleanField(default=False)),
                ('language', models.CharField(default='ru', max_length=10)),
                ('estimated_weeks', models.SmallIntegerField(blank=True, null=True)),
                ('is_sequential', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_courses', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning', to='learning.coursecategory')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
                'db_table': 'courses_course',
            },
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('dropped', 'Dropped')], default='active', max_length=20)),
                ('delivery_format', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], max_length=10)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('dropped_at', models.DateTimeField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='enrollments', to='learning.course')),
                ('enrolled_by', models.ForeignKey(blank=True, help_text='Null = self-enrolled. Non-null = admin/mentor enrolled this student.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments_created', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='course_enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course Enrollment',
                'verbose_name_plural': 'Course Enrollments',
                'db_table': 'courses_courseenrollment',
            },
        ),
        migrations.CreateModel(
            name='LessonContent',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('video', 'Video'), ('pdf', 'PDF'), ('slides', 'Slides'), ('text', 'Text'), ('link', 'Link'), ('recording', 'Recording'), ('code', 'Code')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.SmallIntegerField()),
                ('url', models.TextField(blank=True, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('duration_seconds', models.IntegerField(blank=True, help_text="Used for video and recording. Shown in UI as '12 min'.", null=True)),
                ('file_size_bytes', models.BigIntegerField(blank=True, help_text='Used for pdf and downloadable files.', null=True)),
                ('metadata', models.JSONField(default=dict, help_text='Type-specific extras. Never queried via SQL — read at application level.')),
                ('is_required', models.BooleanField(default=True, help_text='If true, UserProgress domain must record this item as viewed before the lesson is considered complete.')),
                ('is_downloadable', models.BooleanField(default=False, help_text='Meaningful for pdf, slides, recording. Controls download button.')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='learning.lesson')),
            ],
            options={
                'verbose_name': 'Lesson Content',
                'verbose_name_plural': 'Lesson Contents',
                'db_table': 'courses_lessoncontent',
            },
        ),
        migrations.CreateModel(
            name='LessonHomework',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('instructions', models.TextField(blank=True, help_text='Step-by-step guide, acceptance criteria, hints for where to start.', null=True)),
                ('max_score', models.SmallIntegerField(default=100)),
                ('deadline_offset_days', models.SmallIntegerField(blank=True, help_text='Days after lesson unlock. Null = no deadline.', null=True)),
                ('submission_type', models.CharField(choices=[('file', 'File'), ('link', 'Link'), ('text', 'Text'), ('mixed', 'Mixed')], default='file', max_length=20)),
                ('allowed_file_types', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, help_text="e.g. ['pdf', 'zip', 'docx']. Empty list = any type allowed.")),
                ('max_file_size_mb', models.SmallIntegerField(default=20)),
                ('lesson', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='homework', to='learning.lesson')),
            ],
            options={
                'verbose_name': 'Lesson Homework',
                'verbose_name_plural': 'Lesson Homeworks',
                'db_table': 'courses_lessonhomework',
            },
        ),
        migrations.CreateModel(
            name='LessonPractice',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.SmallIntegerField()),
                ('type', models.CharField(choices=[('coding', 'Coding'), ('written', 'Written'), ('interactive', 'Interactive')], default='coding', max_length=20)),
                ('instructions', models.TextField()),
                ('starter_code', models.TextField(blank=True, help_text="Pre-filled code shown to student. Type 'coding' only.", null=True)),
                ('solution_code', models.TextField(blank=True, help_text="Reference solution. Never exposed to students. Type 'coding' only.", null=True)),
                ('language', models.CharField(blank=True, help_text="Programming language for 'coding' type. e.g. 'python', 'javascript'.", max_length=30, null=True)),
                ('hints', models.JSONField(default=list, help_text='Ordered list of hint strings revealed progressively.')),
                ('max_score', models.SmallIntegerField(default=100)),
                ('time_limit_minutes', models.SmallIntegerField(blank=True, help_text='Null = untimed.', null=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practices', to='learning.lesson')),
            ],
            options={
                'verbose_name': 'Lesson Practice',
                'verbose_name_plural': 'Lesson Practices',
                'db_table': 'courses_lessonpractice',
            },
        ),
        migrations.CreateModel(
            name='LessonQuiz',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('time_limit_minutes', models.SmallIntegerField(blank=True, help_text='Null = untimed. Timer enforced by Assessment domain.', null=True)),
                ('pass_score', models.SmallIntegerField(default=70, help_text='Percentage threshold (0–100) to pass.')),
                ('max_attempts', models.SmallIntegerField(blank=True, help_text='Null = unlimited retakes. Enforced by Assessment domain.', null=True)),
                ('shuffle_questions', models.BooleanField(default=False)),
                ('shuffle_options', models.BooleanField(default=False)),
                ('show_correct_after_attempt', models.BooleanField(default=True, help_text='Show correct answers + explanations after submitting. False for high-stakes quizzes.')),
                ('lesson', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quiz', to='learning.lesson')),
            ],
            options={
                'verbose_name': 'Lesson Quiz',
                'verbose_name_plural': 'Lesson Quizzes',
                'db_table': 'courses_lessonquiz',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.SmallIntegerField()),
                ('is_published', models.BooleanField(default=False)),
                ('estimated_hours', models.SmallIntegerField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='learning.course')),
            ],
            options={
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
                'db_table': 'courses_module',
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='learning.module'),
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('single_choice', 'Single Choice'), ('multiple_choice', 'Multiple Choice'), ('true_false', 'True / False'), ('short_text', 'Short Text')], max_length=20)),
                ('body', models.TextField(help_text='Question text. Markdown supported.')),
                ('explanation', models.TextField(blank=True, help_text='Shown after answering (if show_correct_after_attempt = true).', null=True)),
                ('order', models.SmallIntegerField()),
                ('points', models.SmallIntegerField(default=1, help_text='Points awarded for correct answer. Enables weighted questions.')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='learning.lessonquiz')),
            ],
            options={
                'verbose_name': 'Quiz Question',
                'verbose_name_plural': 'Quiz Questions',
                'db_table': 'courses_quizquestion',
            },
        ),
        migrations.CreateModel(
            name='QuizOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField()),
                ('is_correct', models.BooleanField()),
                ('order', models.SmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='learning.quizquestion')),
            ],
            options={
                'verbose_name': 'Quiz Option',
                'verbose_name_plural': 'Quiz Options',
                'db_table': 'courses_quizoption',
            },
        ),
        migrations.AddIndex(
            model_name='coursecategory',
            index=models.Index(condition=models.Q(('is_active', True)), fields=['parent_id', 'order'], name='idx_category_root'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(condition=models.Q(('deleted_at__isnull', True)), fields=['status'], name='idx_course_status'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(condition=models.Q(('deleted_at__isnull', True)), fields=['category_id'], name='idx_course_category'),
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['draft', 'published', 'archived'])), name='chk_course_status'),
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.CheckConstraint(condition=models.Q(('estimated_weeks__isnull', True), ('estimated_weeks__gt', 0), _connector='OR'), name='chk_course_weeks'),
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.CheckConstraint(condition=models.Q(('supports_online', True), ('supports_offline', True), _connector='OR'), name='chk_course_delivery'),
        ),
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['user_id', 'status'], name='idx_courseenrollment_user_status'),
        ),
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['course_id', 'status'], name='idx_courseenrollment_course_status'),
        ),
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.UniqueConstraint(fields=('user_id', 'course_id'), name='uq_courseenrollment_user_course'),
        ),
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['active', 'completed', 'dropped'])), name='chk_enrollment_status'),
        ),
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.CheckConstraint(condition=models.Q(('delivery_format__in', ['online', 'offline'])), name='chk_enrollment_delivery_format'),
        ),
        migrations.AddIndex(
            model_name='lessoncontent',
            index=models.Index(fields=['lesson_id', 'order'], name='idx_content_lesson'),
        ),
        migrations.AddIndex(
            model_name='lessoncontent',
            index=models.Index(fields=['type', 'lesson_id'], name='idx_content_type'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.UniqueConstraint(fields=('lesson_id', 'order'), name='uq_content_lesson_order'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.CheckConstraint(condition=models.Q(('type__in', ['video', 'pdf', 'slides', 'text', 'link', 'recording', 'code'])), name='chk_content_type'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.CheckConstraint(condition=models.Q(('url__isnull', False), ('body__isnull', False), _connector='OR'), name='chk_content_has_source'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_content_order_positive'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.CheckConstraint(condition=models.Q(('duration_seconds__isnull', True), ('duration_seconds__gt', 0), _connector='OR'), name='chk_content_duration'),
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.CheckConstraint(condition=models.Q(('file_size_bytes__isnull', True), ('file_size_bytes__gt', 0), _connector='OR'), name='chk_content_file_size'),
        ),
        migrations.AddConstraint(
            model_name='lessonhomework',
            constraint=models.CheckConstraint(condition=models.Q(('submission_type__in', ['file', 'link', 'text', 'mixed'])), name='chk_homework_submission_type'),
        ),
        migrations.AddConstraint(
            model_name='lessonhomework',
            constraint=models.CheckConstraint(condition=models.Q(('max_score__gt', 0)), name='chk_homework_max_score'),
        ),
        migrations.AddConstraint(
            model_name='lessonhomework',
            constraint=models.CheckConstraint(condition=models.Q(('deadline_offset_days__isnull', True), ('deadline_offset_days__gt', 0), _connector='OR'), name='chk_homework_deadline_offset'),
        ),
        migrations.AddConstraint(
            model_name='lessonhomework',
            constraint=models.CheckConstraint(condition=models.Q(('max_file_size_mb__gt', 0)), name='chk_homework_file_size'),
        ),
        migrations.AddConstraint(
            model_name='lessonpractice',
            constraint=models.UniqueConstraint(fields=('lesson_id', 'order'), name='uq_practice_lesson_order'),
        ),
        migrations.AddConstraint(
            model_name='lessonpractice',
            constraint=models.CheckConstraint(condition=models.Q(('type__in', ['coding', 'written', 'interactive'])), name='chk_practice_type'),
        ),
        migrations.AddConstraint(
            model_name='lessonpractice',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_practice_order_positive'),
        ),
        migrations.AddConstraint(
            model_name='lessonpractice',
            constraint=models.CheckConstraint(condition=models.Q(('max_score__gt', 0)), name='chk_practice_max_score'),
        ),
        migrations.AddConstraint(
            model_name='lessonpractice',
            constraint=models.CheckConstraint(condition=models.Q(('time_limit_minutes__isnull', True), ('time_limit_minutes__gt', 0), _connector='OR'), name='chk_practice_time_limit'),
        ),
        migrations.AddConstraint(
            model_name='lessonquiz',
            constraint=models.CheckConstraint(condition=models.Q(('pass_score__gte', 0), ('pass_score__lte', 100)), name='chk_quiz_pass_score'),
        ),
        migrations.AddConstraint(
            model_name='lessonquiz',
            constraint=models.CheckConstraint(condition=models.Q(('time_limit_minutes__isnull', True), ('time_limit_minutes__gt', 0), _connector='OR'), name='chk_quiz_time_limit'),
        ),
        migrations.AddConstraint(
            model_name='lessonquiz',
            constraint=models.CheckConstraint(condition=models.Q(('max_attempts__isnull', True), ('max_attempts__gt', 0), _connector='OR'), name='chk_quiz_max_attempts'),
        ),
        migrations.AddIndex(
            model_name='module',
            index=models.Index(condition=models.Q(('deleted_at__isnull', True), ('is_published', True)), fields=['course_id', 'order'], name='idx_module_course_published'),
        ),
        migrations.AddConstraint(
            model_name='module',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted_at__isnull', True)), fields=('course_id', 'order'), name='uq_module_course_order'),
        ),
        migrations.AddConstraint(
            model_name='module',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_module_order_positive'),
        ),
        migrations.AddConstraint(
            model_name='module',
            constraint=models.CheckConstraint(condition=models.Q(('estimated_hours__isnull', True), ('estimated_hours__gt', 0), _connector='OR'), name='chk_module_estimated_hours'),
        ),
        migrations.AddIndex(
            model_name='lesson',
            index=models.Index(condition=models.Q(('deleted_at__isnull', True), ('is_published', True)), fields=['module_id', 'order'], name='idx_lesson_module_published'),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted_at__isnull', True)), fields=('module_id', 'order'), name='uq_lesson_module_order'),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_lesson_order_positive'),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.CheckConstraint(condition=models.Q(('estimated_minutes__isnull', True), ('estimated_minutes__gt', 0), _connector='OR'), name='chk_lesson_estimated_minutes'),
        ),
        migrations.AddConstraint(
            model_name='quizquestion',
            constraint=models.UniqueConstraint(fields=('quiz_id', 'order'), name='uq_question_quiz_order'),
        ),
        migrations.AddConstraint(
            model_name='quizquestion',
            constraint=models.CheckConstraint(condition=models.Q(('type__in', ['single_choice', 'multiple_choice', 'true_false', 'short_text'])), name='chk_question_type'),
        ),
        migrations.AddConstraint(
            model_name='quizquestion',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_question_order_positive'),
        ),
        migrations.AddConstraint(
            model_name='quizquestion',
            constraint=models.CheckConstraint(condition=models.Q(('points__gt', 0)), name='chk_question_points_positive'),
        ),
        migrations.AddConstraint(
            model_name='quizoption',
            constraint=models.UniqueConstraint(fields=('question_id', 'order'), name='uq_option_question_order'),
        ),
        migrations.AddConstraint(
            model_name='quizoption',
            constraint=models.CheckConstraint(condition=models.Q(('order__gt', 0)), name='chk_option_order_positive'),
        ),
    ]
