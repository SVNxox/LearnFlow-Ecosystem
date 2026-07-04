

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial_empty'),
        ('learning', '0002_move_enrollment_to_new_domain'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='CourseEnrollment',
                    fields=[
                        ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ('course_id', models.UUIDField(db_index=True)),
                        ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('dropped', 'Dropped')], default='active', max_length=20)),
                        ('delivery_format', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], max_length=10)),
                        ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                        ('completed_at', models.DateTimeField(blank=True, null=True)),
                        ('dropped_at', models.DateTimeField(blank=True, null=True)),
                        ('enrolled_by', models.ForeignKey(blank=True, help_text='Null = self-enrolled. Non-null = admin/mentor enrolled this student.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments_created', to=settings.AUTH_USER_MODEL)),
                        ('user', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.PROTECT, related_name='course_enrollments', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'verbose_name': 'Course Enrollment',
                        'verbose_name_plural': 'Course Enrollments',
                        'db_table': 'enrollment_courseenrollment',
                        'indexes': [
                            models.Index(fields=['user_id', 'status'], name='idx_enrollment_user_status'),
                            models.Index(fields=['course_id', 'status'], name='idx_enrollment_course_status'),
                        ],
                        'constraints': [
                            models.UniqueConstraint(fields=['user_id', 'course_id'], name='uq_enrollment_user_course'),
                            models.CheckConstraint(condition=models.Q(status__in=['active', 'completed', 'dropped']), name='chk_enrollment_status'),
                            models.CheckConstraint(condition=models.Q(delivery_format__in=['online', 'offline']), name='chk_enrollment_delivery_format'),
                        ],
                    },
                ),
            ],
            database_operations=[],  
        ),
    ]
