

import django.db.models.constraints
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0004_course_currency_course_price'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='lessoncontent',
            name='uq_content_lesson_order',
        ),
        migrations.AddConstraint(
            model_name='lessoncontent',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('lesson_id', 'order'), name='uq_content_lesson_order'),
        ),
    ]
