

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('student', 'Student'), ('mentor', 'Mentor'), ('staff', 'Staff'), ('admin', 'Admin')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'accounts_role',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('failed_login_attempts', models.PositiveSmallIntegerField(default=0)),
                ('locked_until', models.DateTimeField(blank=True, null=True)),
                ('last_login_at', models.DateTimeField(blank=True, null=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'accounts_user',
                'indexes': [models.Index(condition=models.Q(('is_active', True), ('is_blocked', False)), fields=['is_active', 'is_blocked'], name='idx_user_active_auth')],
            },
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('expires_at', models.DateTimeField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_verification_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_emailverificationtoken',
            },
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('expires_at', models.DateTimeField()),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_reset_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_passwordresettoken',
            },
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_date', models.DateField(default=django.utils.timezone.now)),
                ('streak_days', models.PositiveSmallIntegerField(default=0)),
                ('total_xp', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mentor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentees', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_studentprofile',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(default='', max_length=100)),
                ('last_name', models.CharField(default='', max_length=100)),
                ('avatar_url', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('bio', models.TextField(blank=True, max_length=1000, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_userinfo',
            },
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('language', models.CharField(default='ru', max_length=10)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('notify_email', models.BooleanField(default=True)),
                ('notify_telegram', models.BooleanField(default=True)),
                ('notify_web', models.BooleanField(default=True)),
                ('notify_deadlines', models.BooleanField(default=True)),
                ('notify_grades', models.BooleanField(default=True)),
                ('notify_mentor_comments', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_usersettings',
            },
        ),
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email_used', models.EmailField(max_length=254)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('failure_reason', models.CharField(blank=True, max_length=100, null=True)),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='login_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_loginattempt',
                'indexes': [models.Index(fields=['ip_address', '-attempted_at'], name='idx_loginattempt_ip'), models.Index(fields=['user', '-attempted_at'], name='idx_loginattempt_user')],
            },
        ),
        migrations.CreateModel(
            name='MentorProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('specialization', models.JSONField(default=list)),
                ('max_students', models.PositiveSmallIntegerField(default=20)),
                ('current_student_count', models.PositiveSmallIntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('joined_as_mentor_at', models.DateField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_mentorprofile',
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 0), ('rating__lte', 5)), name='chk_rating_range'), models.CheckConstraint(condition=models.Q(('max_students__gt', 0)), name='chk_max_students'), models.CheckConstraint(condition=models.Q(('current_student_count__lte', models.F('max_students'))), name='chk_capacity')],
            },
        ),
        migrations.CreateModel(
            name='RefreshToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('device_name', models.CharField(blank=True, max_length=200, null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refresh_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_refreshtoken',
                'indexes': [models.Index(condition=models.Q(('revoked_at__isnull', True)), fields=['user', '-created_at'], name='idx_refreshtoken_user_active')],
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_roles', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='user_roles', to='identity.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_userrole',
                'constraints': [models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('user', 'role'), name='uq_userrole_active')],
            },
        ),
    ]
