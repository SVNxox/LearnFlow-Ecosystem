import uuid
import secrets
import hashlib
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models, transaction
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=254)

    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "accounts_user"
        indexes = [
            models.Index(
                fields=["is_active", "is_blocked"],
                name="idx_user_active_auth",
                condition=models.Q(is_active=True, is_blocked=False),
            ),
        ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def get_roles(self):
        return list(
            self.user_roles.filter(is_active=True).values_list("role__name", flat=True)
        )

    def has_role(self, role_name: str) -> bool:
        """Проверить, есть ли у пользователя конкретная роль."""
        return self.user_roles.filter(role__name=role_name, is_active=True).exists()

    def has_any_role(self, role_names: list[str]) -> bool:
        return self.user_roles.filter(role__name__in=role_names, is_active=True).exists()


class UserInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="info")

    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    avatar_url = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True, max_length=1000)
    date_of_birth = models.DateField(null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_userinfo"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or str(self.user_id)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip()
        self.last_name  = self.last_name.strip()
        super().save(*args, **kwargs)


class Role(models.Model):
    STUDENT = "student"
    MENTOR = "mentor"
    STAFF = "staff"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (MENTOR, "Mentor"),
        (STAFF, "Staff"),
        (ADMIN, "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_role"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, related_name="user_roles")
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_roles"
    )

    class Meta:
        db_table = "accounts_userrole"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                condition=models.Q(is_active=True),
                name="uq_userrole_active",
            )
        ]

    def __str__(self):
        return f"{self.user_id} → {self.role.name}"


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")

    enrollment_date = models.DateField(default=timezone.now)
    streak_days = models.PositiveSmallIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    mentor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mentees"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_studentprofile"

    def __str__(self):
        return f"StudentProfile({self.user_id})"


class MentorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor_profile")

    specialization = models.JSONField(default=list)
    max_students = models.PositiveSmallIntegerField(default=30)
    current_student_count = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    joined_as_mentor_at = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_mentorprofile"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=0, rating__lte=5),
                name="chk_rating_range",
            ),
            models.CheckConstraint(
                condition=models.Q(max_students__gt=0),
                name="chk_max_students",
            ),
            models.CheckConstraint(
                condition=models.Q(current_student_count__lte=models.F("max_students")),
                name="chk_capacity",
            ),
        ]

    def __str__(self):
        return f"MentorProfile({self.user_id})"


class UserSettings(models.Model):
    UZ = "uz"
    RU = "ru"
    EN = "en"

    LANGUAGE_CHOICES = [
        (UZ, "O'zbekcha"),
        (RU, "Русский"),
        (EN, "English"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")

    language = models.CharField(max_length=10,choices=LANGUAGE_CHOICES, default="uz")
    timezone = models.CharField(max_length=50, default="UTC")

    notify_email = models.BooleanField(default=True)
    notify_telegram = models.BooleanField(default=True)
    notify_web = models.BooleanField(default=True)
    notify_deadlines = models.BooleanField(default=True)
    notify_grades = models.BooleanField(default=True)
    notify_mentor_comments = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_usersettings"

    def __str__(self):
        return f"UserSettings({self.user_id})"


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")

    token_hash = models.CharField(max_length=64, unique=True)

    device_name = models.CharField(max_length=200, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)

    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_refreshtoken"
        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="idx_refreshtoken_user_active",
                condition=models.Q(revoked_at__isnull=True),
            ),
        ]

    def __str__(self):
        return f"RefreshToken({self.user_id}, expires={self.expires_at})"

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()

    def revoke(self):
        self.revoked_at = timezone.now()
        self.save(update_fields=["revoked_at"])

    @classmethod
    def create_for_user(cls, user, ip_address, user_agent=None, device_name=None):
        raw_token = secrets.token_urlsafe(48)
        instance = cls.objects.create(
            user=user,
            token_hash=_sha256(raw_token),
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            expires_at=timezone.now() + timedelta(days=30),
        )
        return raw_token, instance

    @classmethod
    def get_by_raw(cls, raw_token):
        token_hash = _sha256(raw_token)
        try:
            return cls.objects.select_related("user").get(token_hash=token_hash)
        except cls.DoesNotExist:
            return None


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")

    token_hash = models.CharField(max_length=64, unique=True)

    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_passwordresettoken"

    def __str__(self):
        return f"PasswordResetToken({self.user_id})"

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    @classmethod
    def create_for_user(cls, user):
        cls.objects.filter(user=user, used_at__isnull=True).update(
            used_at=timezone.now()
        )
        raw_token = secrets.token_urlsafe(32)
        instance = cls.objects.create(
            user=user,
            token_hash=_sha256(raw_token),
            expires_at=timezone.now() + timedelta(hours=1),
        )
        return raw_token, instance

    @classmethod
    def get_by_raw(cls, raw_token):
        token_hash = _sha256(raw_token)
        try:
            return cls.objects.select_related("user").get(token_hash=token_hash)
        except cls.DoesNotExist:
            return None


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")

    token_hash = models.CharField(max_length=64, unique=True)

    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_emailverificationtoken"

    def __str__(self):
        return f"EmailVerificationToken({self.user_id})"

    @property
    def is_valid(self):
        return self.verified_at is None and self.expires_at > timezone.now()

    @classmethod
    def create_for_user(cls, user):
        cls.objects.filter(user=user, verified_at__isnull=True).update(
            verified_at=timezone.now()
        )
        raw_token = secrets.token_urlsafe(32)
        instance = cls.objects.create(
            user=user,
            token_hash=_sha256(raw_token),
            expires_at=timezone.now() + timedelta(hours=24),
        )
        return raw_token, instance

    @classmethod
    def get_by_raw(cls, raw_token):
        token_hash = _sha256(raw_token)
        try:
            return cls.objects.select_related("user").get(token_hash=token_hash)
        except cls.DoesNotExist:
            return None


class LoginAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="login_attempts"
    )

    email_used = models.EmailField(max_length=254)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)

    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, null=True, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_loginattempt"
        indexes = [
            models.Index(fields=["ip_address", "-attempted_at"], name="idx_loginattempt_ip"),
            models.Index(fields=["user", "-attempted_at"], name="idx_loginattempt_user"),
        ]

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        return f"LoginAttempt({self.email_used}, {status}, {self.ip_address})"


@receiver(post_save, sender=User)
def create_user_related(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            UserInfo.objects.get_or_create(user=instance)
            UserSettings.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserRole)
def create_role_profile(sender, instance, created, **kwargs):
    if created and instance.is_active:
        if instance.role.name == Role.STUDENT:
            StudentProfile.objects.get_or_create(user=instance.user)

        elif instance.role.name == Role.MENTOR:
            MentorProfile.objects.get_or_create(user=instance.user)