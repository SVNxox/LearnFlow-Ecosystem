"""
Create default roles for the system.

This migration ensures that the required roles exist before any user registration.
"""
from django.db import migrations


def create_default_roles(apps, schema_editor):
    """Create Student, Mentor, Staff, and Admin roles."""
    Role = apps.get_model('identity', 'Role')

    roles = [
        ('student', 'Default student role - can enroll in courses and submit work'),
        ('mentor', 'Course mentor role - can review submissions and grade assessments'),
        ('staff', 'Staff member role - can create and manage courses'),
        ('admin', 'Administrator role - full system access'),
    ]

    for name, description in roles:
        Role.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )


def reverse_default_roles(apps, schema_editor):
    """Remove default roles (only if no users have them)."""
    Role = apps.get_model('identity', 'Role')
    UserRole = apps.get_model('identity', 'UserRole')

    
    for role_name in ['student', 'mentor', 'staff', 'admin']:
        try:
            role = Role.objects.get(name=role_name)
            if not UserRole.objects.filter(role=role).exists():
                role.delete()
        except Role.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(create_default_roles, reverse_default_roles),
    ]
