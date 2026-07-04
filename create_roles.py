
"""Create default roles if they don't exist."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnflow.settings.development')
django.setup()

from src.backend.identity.models import Role

roles_to_create = [
    (Role.STUDENT, "Student - enrolled in courses"),
    (Role.MENTOR, "Mentor - reviews submissions and provides guidance"),
    (Role.STAFF, "Staff - manages courses and content"),
    (Role.ADMIN, "Admin - full system access"),
]

for role_name, description in roles_to_create:
    role, created = Role.objects.get_or_create(
        name=role_name,
        defaults={'description': description}
    )
    if created:
        print(f"✓ Created role: {role_name}")
    else:
        print(f"• Role already exists: {role_name}")

print(f"\nTotal roles in database: {Role.objects.count()}")
