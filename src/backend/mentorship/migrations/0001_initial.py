

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
            name='MentorGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course_id', models.UUIDField(help_text='Course ID (soft reference)')),
                ('name', models.CharField(help_text="Group name (e.g., 'Python Backend 
                ('planned_lessons_count', models.SmallIntegerField(help_text='Planned number of lessons')),
                ('max_students', models.SmallIntegerField(default=30, help_text='Maximum students in this group')),
                ('current_students_count', models.SmallIntegerField(default=0, help_text='Current number of students')),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('archived', 'Archived')], default='active', help_text='Group status', max_length=20)),
                ('started_at', models.DateTimeField(blank=True, help_text='When the group started', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='When the group completed', null=True)),
                ('mentor', models.ForeignKey(help_text='Mentor leading this group', on_delete=django.db.models.deletion.PROTECT, related_name='mentor_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mentorship_mentorgroup',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OfflineSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lesson_id', models.UUIDField(blank=True, help_text='Lesson ID (soft reference, can be NULL for custom sessions)', null=True)),
                ('module_id', models.UUIDField(blank=True, help_text='Module ID (denormalized for queries)', null=True)),
                ('title', models.CharField(help_text="Session title (e.g., 'Занятие 5: Django ORM')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Session description', null=True)),
                ('scheduled_start', models.DateTimeField(help_text='Scheduled start time')),
                ('scheduled_end', models.DateTimeField(help_text='Scheduled end time')),
                ('actual_start', models.DateTimeField(blank=True, help_text='Actual start time', null=True)),
                ('actual_end', models.DateTimeField(blank=True, help_text='Actual end time', null=True)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('rescheduled', 'Rescheduled')], default='scheduled', help_text='Session status', max_length=20)),
                ('location', models.CharField(blank=True, help_text="Physical location (e.g., 'Room 301')", max_length=255, null=True)),
                ('meeting_url', models.TextField(blank=True, help_text='Online meeting URL (Zoom, Google Meet)', null=True)),
                ('notes', models.TextField(blank=True, help_text='Mentor notes', null=True)),
                ('group', models.ForeignKey(help_text='Mentor group for this session', on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='mentorship.mentorgroup')),
            ],
            options={
                'db_table': 'mentorship_offlinesession',
                'ordering': ['scheduled_start'],
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')], help_text='Attendance status', max_length=20)),
                ('marked_at', models.DateTimeField(auto_now_add=True, help_text='When attendance was marked')),
                ('notes', models.TextField(blank=True, help_text='Additional notes', null=True)),
                ('marked_by', models.ForeignKey(help_text='Mentor who marked attendance', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marked_attendances', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(help_text='Student', on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(help_text='Session this attendance belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='mentorship.offlinesession')),
            ],
            options={
                'db_table': 'mentorship_attendance',
                'ordering': ['-marked_at'],
            },
        ),
        migrations.CreateModel(
            name='StudentMentorGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(help_text='Enrollment ID (soft reference)')),
                ('joined_at', models.DateTimeField(auto_now_add=True, help_text='When student joined the group')),
                ('left_at', models.DateTimeField(blank=True, help_text='When student left the group', null=True)),
                ('group', models.ForeignKey(help_text='Mentor group', on_delete=django.db.models.deletion.CASCADE, related_name='student_memberships', to='mentorship.mentorgroup')),
                ('student', models.ForeignKey(help_text='Student in this group', on_delete=django.db.models.deletion.CASCADE, related_name='mentor_group_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mentorship_studentmentorgroup',
                'ordering': ['joined_at'],
            },
        ),
        migrations.CreateModel(
            name='AccessEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('entered_at', models.DateTimeField(help_text='When student entered')),
                ('exited_at', models.DateTimeField(blank=True, help_text='When student exited', null=True)),
                ('source', models.CharField(choices=[('face_id', 'Face ID'), ('rfid', 'RFID Card'), ('turnstile', 'Turnstile'), ('manual', 'Manual Entry')], help_text='Access source', max_length=20)),
                ('device_id', models.CharField(blank=True, help_text='Device ID (turnstile, face_id reader)', max_length=100, null=True)),
                ('location', models.CharField(blank=True, help_text='Location (building, floor)', max_length=100, null=True)),
                ('metadata', models.JSONField(default=dict, help_text='Additional metadata')),
                ('student', models.ForeignKey(help_text='Student who accessed', on_delete=django.db.models.deletion.CASCADE, related_name='access_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mentorship_accessevent',
                'ordering': ['-entered_at'],
                'indexes': [models.Index(fields=['student', 'entered_at'], name='idx_access_student'), models.Index(fields=['entered_at'], name='idx_access_time')],
            },
        ),
        migrations.AddIndex(
            model_name='mentorgroup',
            index=models.Index(fields=['mentor', 'status'], name='idx_group_mentor_status'),
        ),
        migrations.AddIndex(
            model_name='mentorgroup',
            index=models.Index(fields=['course_id', 'status'], name='idx_group_course'),
        ),
        migrations.AddConstraint(
            model_name='mentorgroup',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['active', 'completed', 'archived'])), name='chk_group_status'),
        ),
        migrations.AddConstraint(
            model_name='mentorgroup',
            constraint=models.CheckConstraint(condition=models.Q(('current_students_count__lte', models.F('max_students'))), name='chk_group_capacity'),
        ),
        migrations.AddIndex(
            model_name='offlinesession',
            index=models.Index(fields=['group', 'scheduled_start'], name='idx_session_group'),
        ),
        migrations.AddIndex(
            model_name='offlinesession',
            index=models.Index(fields=['lesson_id', 'group'], name='idx_session_lesson'),
        ),
        migrations.AddIndex(
            model_name='offlinesession',
            index=models.Index(fields=['status', 'scheduled_start'], name='idx_session_status'),
        ),
        migrations.AddConstraint(
            model_name='offlinesession',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled'])), name='chk_session_status'),
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['session', 'student'], name='idx_attendance_session'),
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['student', 'status'], name='idx_attendance_student'),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(fields=('session', 'student'), name='uq_attendance_session_student'),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['present', 'absent', 'late', 'excused'])), name='chk_attendance_status'),
        ),
        migrations.AddIndex(
            model_name='studentmentorgroup',
            index=models.Index(fields=['student', 'group'], name='idx_student_group'),
        ),
        migrations.AddIndex(
            model_name='studentmentorgroup',
            index=models.Index(fields=['group', 'joined_at'], name='idx_group_students'),
        ),
        migrations.AddIndex(
            model_name='studentmentorgroup',
            index=models.Index(fields=['enrollment_id'], name='idx_membership_enrollment'),
        ),
        migrations.AddConstraint(
            model_name='studentmentorgroup',
            constraint=models.UniqueConstraint(condition=models.Q(('left_at__isnull', True)), fields=('student', 'group'), name='uq_active_student_group'),
        ),
    ]
