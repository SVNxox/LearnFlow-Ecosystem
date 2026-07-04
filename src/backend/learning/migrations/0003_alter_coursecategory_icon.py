

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_move_enrollment_to_new_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecategory',
            name='icon',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
