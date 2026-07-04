
"""Create a test user for frontend testing."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnflow.settings.development')
django.setup()

from src.backend.identity.domain.models.user import User


email = "test@example.com"
password = "testpass123"


if User.objects.filter(email=email).exists():
    print(f"User {email} already exists")
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_active = True
    user.email_verified = True
    user.save()
    print(f"Password updated for {email}")
else:
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        is_active=True,
        email_verified=True
    )
    print(f"Created user: {email}")

print(f"\nTest credentials:")
print(f"Email: {email}")
print(f"Password: {password}")
