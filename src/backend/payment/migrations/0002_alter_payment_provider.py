

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='provider',
            field=models.CharField(choices=[('stripe', 'Stripe'), ('payme', 'Payme.uz'), ('click', 'Click.uz'), ('manual', 'Manual')], max_length=20),
        ),
    ]
