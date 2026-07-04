

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DomainEventOutbox',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(db_index=True, max_length=100)),
                ('aggregate_id', models.UUIDField(db_index=True)),
                ('payload', models.JSONField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('processed', 'Processed'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
                ('retry_count', models.PositiveSmallIntegerField(default=0)),
                ('max_retries', models.PositiveSmallIntegerField(default=5)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Domain Event Outbox',
                'verbose_name_plural': 'Domain Events Outbox',
                'db_table': 'shared_domaineventoutbox',
                'ordering': ['created_at'],
                'indexes': [models.Index(fields=['status', 'created_at'], name='idx_outbox_pending'), models.Index(fields=['aggregate_id', 'created_at'], name='idx_outbox_aggregate')],
            },
        ),
    ]
