
"""
Quick script to grant admin role to a user.
Usage: python grant_admin.py <email>
"""
import os
import sys
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnflow.settings.local')
django.setup()

from src.backend.identity.models import User, Role, UserRole

def grant_admin_role(email):
    try:
        user = User.objects.get(email=email)
        admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)

        if user.has_role('admin'):
            print(f"✓ User {email} already has admin role")
        else:
            UserRole.objects.create(user=user, role=admin_role, is_active=True)
            print(f"✓ Admin role granted to {email}")

        print(f"\nCurrent roles: {', '.join(user.get_roles())}")

    except User.DoesNotExist:
        print(f"✗ User with email {email} not found")
        print("\nAvailable users:")
        for u in User.objects.all()[:5]:
            roles = ', '.join(u.get_roles()) or 'no roles'
            print(f"  - {u.email} ({roles})")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python grant_admin.py <email>")
        print("\nAvailable users:")
        for u in User.objects.all()[:5]:
            roles = ', '.join(u.get_roles()) or 'no roles'
            print(f"  - {u.email} ({roles})")
        sys.exit(1)

    grant_admin_role(sys.argv[1])
