

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_alter_coursecategory_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='currency',
            field=models.CharField(choices=[('UZS', 'UZS'), ('USD', 'USD')], default='UZS', max_length=3),
        ),
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Course price (0 for free courses)', max_digits=10),
        ),
    ]
