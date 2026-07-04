import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnflow.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = 'verified@example.com'
password = 'testpass123'


User.objects.filter(email=email).delete()


user = User.objects.create_user(
    email=email,
    password=password,
    is_active=True  
)


user.info.first_name = 'Verified'
user.info.last_name = 'User'
user.info.save()

print(f"Created verified user: {email}")
print(f"Password: {password}")
print(f"Is active (verified): {user.is_active}")
print(f"Name: {user.info.first_name} {user.info.last_name}")
