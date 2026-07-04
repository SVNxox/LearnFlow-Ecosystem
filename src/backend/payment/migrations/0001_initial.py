

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrollment_id', models.UUIDField(db_index=True)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Payment amount', max_digits=10)),
                ('currency', models.CharField(default='USD', help_text='ISO 4217 currency code', max_length=3)),
                ('provider', models.CharField(choices=[('stripe', 'Stripe'), ('payme', 'Payme.uz'), ('manual', 'Manual')], max_length=20)),
                ('provider_payment_id', models.CharField(blank=True, help_text='Payment ID from provider (Stripe, Payme)', max_length=255, null=True, unique=True)),
                ('provider_customer_id', models.CharField(blank=True, help_text='Customer ID from provider', max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, choices=[('card', 'Credit/Debit Card'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('click', 'Click (Uzbekistan)'), ('payme', 'Payme (Uzbekistan)')], max_length=20, null=True)),
                ('card_last4', models.CharField(blank=True, help_text='Last 4 digits of card (PCI compliant)', max_length=4, null=True)),
                ('card_brand', models.CharField(blank=True, help_text='Card brand (visa, mastercard, amex)', max_length=20, null=True)),
                ('idempotency_key', models.CharField(help_text='Prevents duplicate charges', max_length=255, unique=True)),
                ('metadata', models.JSONField(default=dict, help_text='Flexible storage for provider-specific data')),
                ('failure_code', models.CharField(blank=True, max_length=50, null=True)),
                ('failure_message', models.TextField(blank=True, null=True)),
                ('succeeded_at', models.DateTimeField(blank=True, null=True)),
                ('failed_at', models.DateTimeField(blank=True, null=True)),
                ('refunded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'db_table': 'payment_payment',
            },
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('created', 'Created'), ('processing', 'Processing'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('provider_response', models.JSONField(blank=True, help_text='Raw response from payment provider', null=True)),
                ('transaction_id', models.CharField(help_text='Unique transaction ID (payment_id:type format)', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='payment.payment')),
            ],
            options={
                'verbose_name': 'Payment Transaction',
                'verbose_name_plural': 'Payment Transactions',
                'db_table': 'payment_transaction',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Refund amount', max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('succeeded', 'Succeeded'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('reason', models.CharField(choices=[('duplicate', 'Duplicate'), ('fraudulent', 'Fraudulent'), ('requested_by_customer', 'Requested by customer'), ('course_cancelled', 'Course cancelled'), ('other', 'Other')], max_length=100)),
                ('reason_details', models.TextField(blank=True, help_text='Additional details about refund reason', null=True)),
                ('provider_refund_id', models.CharField(blank=True, help_text='Refund ID from provider', max_length=255, null=True, unique=True)),
                ('succeeded_at', models.DateTimeField(blank=True, null=True)),
                ('failed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initiated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refunds_initiated', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='refunds', to='payment.payment')),
            ],
            options={
                'verbose_name': 'Refund',
                'verbose_name_plural': 'Refunds',
                'db_table': 'payment_refund',
            },
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['user', 'status'], name='idx_payment_user_status'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['enrollment_id'], name='idx_payment_enrollment'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['provider_payment_id'], name='idx_payment_provider_id'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['idempotency_key'], name='idx_payment_idempotency'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status', 'created_at'], name='idx_payment_status_created'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.CheckConstraint(condition=models.Q(('amount__gt', 0)), name='chk_payment_amount_positive'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded'])), name='chk_payment_status'),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['payment', 'created_at'], name='idx_transaction_payment'),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['transaction_type', 'created_at'], name='idx_transaction_type'),
        ),
        migrations.AddIndex(
            model_name='refund',
            index=models.Index(fields=['payment', 'status'], name='idx_refund_payment_status'),
        ),
        migrations.AddIndex(
            model_name='refund',
            index=models.Index(fields=['provider_refund_id'], name='idx_refund_provider_id'),
        ),
        migrations.AddConstraint(
            model_name='refund',
            constraint=models.CheckConstraint(condition=models.Q(('amount__gt', 0)), name='chk_refund_amount_positive'),
        ),
    ]
