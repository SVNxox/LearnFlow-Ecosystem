"""
Add Enrollment Domain models: AccessRule, EnrollmentPrerequisite
Update CourseEnrollment with new fields
"""

from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0002_register_courseenrollment'),
    ]

    operations = [
        
        migrations.AddField(
            model_name='courseenrollment',
            name='access_level',
            field=models.CharField(
                choices=[('full', 'Full'), ('limited', 'Limited'), ('preview', 'Preview')],
                default='full',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='start_date',
            field=models.DateField(blank=True, help_text='When access begins', null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='end_date',
            field=models.DateField(blank=True, help_text='When access expires', null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='suspended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='suspended_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='dropped_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),

        
        migrations.AlterField(
            model_name='courseenrollment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('active', 'Active'),
                    ('suspended', 'Suspended'),
                    ('dropped', 'Dropped'),
                    ('completed', 'Completed')
                ],
                default='pending',
                max_length=20
            ),
        ),

        
        migrations.AlterField(
            model_name='courseenrollment',
            name='delivery_format',
            field=models.CharField(
                choices=[('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')],
                max_length=10
            ),
        ),

        
        migrations.CreateModel(
            name='AccessRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('resource_type', models.CharField(
                    choices=[('course', 'Course'), ('module', 'Module'), ('lesson', 'Lesson'), ('content', 'Content')],
                    max_length=20
                )),
                ('resource_id', models.UUIDField(db_index=True)),
                ('rule_type', models.CharField(
                    choices=[
                        ('time_based', 'Time-based'),
                        ('prerequisite', 'Prerequisite'),
                        ('payment_tier', 'Payment Tier'),
                        ('delivery_format', 'Delivery Format')
                    ],
                    max_length=30
                )),
                ('rule_config', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enrollment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='access_rules',
                    to='enrollment.courseenrollment'
                )),
            ],
            options={
                'verbose_name': 'Access Rule',
                'verbose_name_plural': 'Access Rules',
                'db_table': 'enrollment_accessrule',
            },
        ),

        
        migrations.CreateModel(
            name='EnrollmentPrerequisite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('course_id', models.UUIDField(db_index=True)),
                ('prerequisite_type', models.CharField(
                    choices=[
                        ('course', 'Course Completion'),
                        ('assessment', 'Assessment Score'),
                        ('certificate', 'Certificate'),
                        ('custom', 'Custom Rule')
                    ],
                    max_length=20
                )),
                ('prerequisite_config', models.JSONField(default=dict)),
                ('is_required', models.BooleanField(
                    default=True,
                    help_text='False = recommendation only, True = hard requirement'
                )),
                ('order', models.PositiveSmallIntegerField(
                    default=0,
                    help_text='Display order (lower = higher priority)'
                )),
                ('description', models.TextField(blank=True, help_text='Human-readable description shown to students')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Enrollment Prerequisite',
                'verbose_name_plural': 'Enrollment Prerequisites',
                'db_table': 'enrollment_prerequisite',
                'ordering': ['order', 'created_at'],
            },
        ),

        
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['payment_id'], name='idx_enrollment_payment'),
        ),
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['status', 'deleted_at'], name='idx_enrollment_status_deleted'),
        ),
        migrations.AddIndex(
            model_name='accessrule',
            index=models.Index(fields=['enrollment', 'resource_type', 'is_active'], name='idx_accessrule_enr_type'),
        ),
        migrations.AddIndex(
            model_name='accessrule',
            index=models.Index(fields=['resource_id', 'is_active'], name='idx_accessrule_resource'),
        ),
        migrations.AddIndex(
            model_name='enrollmentprerequisite',
            index=models.Index(fields=['course_id', 'is_required'], name='idx_prereq_course_required'),
        ),

        
        migrations.RemoveConstraint(
            model_name='courseenrollment',
            name='chk_enrollment_status',
        ),
        migrations.RemoveConstraint(
            model_name='courseenrollment',
            name='chk_enrollment_delivery_format',
        ),

        
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    status__in=['pending', 'active', 'suspended', 'dropped', 'completed']
                ),
                name='chk_enrollment_status',
            ),
        ),
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.CheckConstraint(
                condition=models.Q(delivery_format__in=['online', 'offline', 'hybrid']),
                name='chk_enrollment_delivery_format',
            ),
        ),
        migrations.AddConstraint(
            model_name='courseenrollment',
            constraint=models.CheckConstraint(
                condition=models.Q(payment_status__in=['pending', 'paid', 'failed', 'refunded']),
                name='chk_enrollment_payment_status',
            ),
        ),
    ]
