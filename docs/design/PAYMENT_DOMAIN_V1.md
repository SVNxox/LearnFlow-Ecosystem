

**Status:** Approved  
**Date:** 2026-06-08  
**Author:** Architecture Team  
**Related ADR:** ADR-032 (mentions Payment as separate domain)

---



**Payment Domain** — отдельный bounded context для обработки платежей, транзакций и возвратов.

**Ключевое отличие от Enrollment:**
- **Payment** = Financial transactions (обработка платежей, refunds, reconciliation)
- **Enrollment** = Access contract (кто имеет доступ, на каких условиях)

**Интеграция:**
```
Student → Payment → Enrollment → Progress
            ↓
        Stripe/Payme
```

**Критичность:** 
- Все события Payment Domain используют **Outbox Pattern** (guaranteed delivery)
- PCI compliance требования
- Финансовый audit trail обязателен

---





| Ответственность           | Описание                                                    |
|---------------------------|-------------------------------------------------------------|
| **Payment Processing**    | Создание и обработка платежей                               |
| **Transaction Management**| Запись всех финансовых операций                             |
| **Refund Processing**     | Возвраты средств                                            |
| **Payment Reconciliation**| Сверка с payment providers                                  |
| **Webhook Handling**      | Обработка webhooks от Stripe/Payme                          |
| **Payment Status Tracking**| pending → processing → succeeded → failed                  |



- ❌ Enrollment management (это Enrollment Domain)
- ❌ Course pricing (это Learning Domain)
- ❌ Certificate generation (это Certificates Domain)
- ❌ Student identity (это Identity Domain)

---





```python

from django.db import models
from shared.domain.base_models import UUIDModel, TimestampedModel

class Payment(UUIDModel, TimestampedModel):
    """
    Aggregate Root: Payment transaction.
    
    Responsibility:
    - Payment lifecycle (pending → succeeded/failed)
    - Link to enrollment
    - Provider-specific data (Stripe, Payme)
    - Idempotency
    """
    
    
    user = models.ForeignKey('identity.User', on_delete=models.PROTECT)
    enrollment_id = models.UUIDField()  
    
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')  
    
    
    provider = models.CharField(
        max_length=20,
        choices=[
            ('stripe', 'Stripe'),
            ('payme', 'Payme.uz'),
            ('manual', 'Manual'),  
        ]
    )
    
    
    provider_payment_id = models.CharField(max_length=255, unique=True, null=True)
    provider_customer_id = models.CharField(max_length=255, null=True)
    
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    
    
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('card', 'Credit/Debit Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash', 'Cash'),
            ('click', 'Click (Uzbekistan)'),
            ('payme', 'Payme (Uzbekistan)'),
        ],
        null=True
    )
    
    
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    card_brand = models.CharField(max_length=20, null=True, blank=True)  
    
    
    idempotency_key = models.CharField(max_length=255, unique=True)
    
    
    metadata = models.JSONField(default=dict)  
    
    
    failure_code = models.CharField(max_length=50, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)
    
    
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_payment'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['enrollment_id']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def is_terminal(self) -> bool:
        """Check if payment is in terminal state."""
        return self.status in ['succeeded', 'failed', 'cancelled', 'refunded']
```

**Таблица:** `payment_payment`

**Индексы:**
- `idx_payment_user_status`
- `idx_payment_enrollment`
- `idx_payment_provider_id`
- `idx_payment_idempotency`
- `idx_payment_status_created`

---



```python

class PaymentTransaction(UUIDModel, TimestampedModel):
    """
    Immutable audit log of all payment state changes.
    
    Every status change = new transaction record.
    """
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
            ('cancelled', 'Cancelled'),
        ]
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    provider_response = models.JSONField(null=True)
    
    
    transaction_id = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = 'payment_transaction'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]
```

**Таблица:** `payment_transaction`

---



```python

class Refund(UUIDModel, TimestampedModel):
    """
    Refund for a payment.
    
    A payment can have multiple partial refunds.
    """
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='refunds'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    reason = models.CharField(
        max_length=100,
        choices=[
            ('duplicate', 'Duplicate'),
            ('fraudulent', 'Fraudulent'),
            ('requested_by_customer', 'Requested by customer'),
            ('course_cancelled', 'Course cancelled'),
            ('other', 'Other'),
        ]
    )
    
    reason_details = models.TextField(null=True, blank=True)
    
    
    provider_refund_id = models.CharField(max_length=255, unique=True, null=True)
    
    
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    
    initiated_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='refunds_initiated'
    )
    
    class Meta:
        db_table = 'payment_refund'
        indexes = [
            models.Index(fields=['payment', 'status']),
            models.Index(fields=['provider_refund_id']),
        ]
```

**Таблица:** `payment_refund`

---



```python

class Subscription(UUIDModel, TimestampedModel):
    """
    Recurring subscription for learning.
    
    v2 feature — monthly/yearly subscriptions.
    """
    
    user = models.ForeignKey('identity.User', on_delete=models.PROTECT)
    
    plan = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ]
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
            ('past_due', 'Past Due'),
            ('expired', 'Expired'),
        ],
        default='active'
    )
    
    
    provider_subscription_id = models.CharField(max_length=255, unique=True)
    
    
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_subscription'
```

---





```python

from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    """Money value object."""
    
    amount: Decimal
    currency: str  
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be ISO 4217 code")
    
    def __str__(self):
        return f"{self.amount} {self.currency}"
    
    def to_cents(self) -> int:
        """Convert to cents (for Stripe API)."""
        return int(self.amount * 100)
```



```python

from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    @property
    def is_terminal(self) -> bool:
        return self in [
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
            PaymentStatus.REFUNDED
        ]
```

---





```python

from django.db import transaction
from payment.domain.models.payment import Payment
from payment.infrastructure.integrations.stripe_client import StripeClient
from shared.infrastructure.outbox.publisher import publish_to_outbox

class PaymentProcessor:
    """Core payment processing logic."""
    
    @staticmethod
    @transaction.atomic
    def create_payment(user, enrollment_id, amount, currency, provider='stripe'):
        """
        Create payment intent.
        
        Returns: Payment
        """
        
        idempotency_key = f"{user.id}:{enrollment_id}:{int(time.time())}"
        
        
        payment = Payment.objects.create(
            user=user,
            enrollment_id=enrollment_id,
            amount=amount,
            currency=currency,
            provider=provider,
            status='pending',
            idempotency_key=idempotency_key,
        )
        
        
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='created',
            amount=amount,
            transaction_id=f"{payment.id}:created",
        )
        
        
        if provider == 'stripe':
            client = StripeClient()
            intent = client.create_payment_intent(
                amount=int(amount * 100),  
                currency=currency,
                metadata={'payment_id': str(payment.id), 'enrollment_id': str(enrollment_id)}
            )
            
            payment.provider_payment_id = intent.id
            payment.save(update_fields=['provider_payment_id'])
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def process_payment_succeeded(payment_id, provider_payment_id):
        """
        Mark payment as succeeded.
        
        Called from webhook handler.
        """
        payment = Payment.objects.select_for_update().get(pk=payment_id)
        
        if payment.is_terminal():
            
            return payment
        
        
        payment.status = 'succeeded'
        payment.succeeded_at = timezone.now()
        payment.save(update_fields=['status', 'succeeded_at'])
        
        
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='succeeded',
            amount=payment.amount,
            transaction_id=f"{payment.id}:succeeded",
        )
        
        
        transaction.on_commit(lambda: publish_to_outbox(
            event_type='PaymentSucceeded',
            aggregate_id=payment.id,
            payload={
                'payment_id': str(payment.id),
                'enrollment_id': str(payment.enrollment_id),
                'user_id': str(payment.user_id),
                'amount': str(payment.amount),
                'currency': payment.currency,
                'occurred_at': timezone.now().isoformat(),
            }
        ))
        
        return payment
```



```python

class RefundProcessor:
    """Refund processing logic."""
    
    @staticmethod
    @transaction.atomic
    def create_refund(payment_id, amount, reason, initiated_by):
        """
        Create refund.
        
        Returns: Refund
        """
        payment = Payment.objects.select_for_update().get(pk=payment_id)
        
        
        if payment.status != 'succeeded':
            raise ValidationError("Can only refund succeeded payments")
        
        
        total_refunded = payment.refunds.filter(
            status='succeeded'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if total_refunded + amount > payment.amount:
            raise ValidationError("Refund amount exceeds payment amount")
        
        
        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            status='pending',
            initiated_by=initiated_by,
        )
        
        
        if payment.provider == 'stripe':
            client = StripeClient()
            provider_refund = client.create_refund(
                payment_intent_id=payment.provider_payment_id,
                amount=int(amount * 100),
            )
            
            refund.provider_refund_id = provider_refund.id
            refund.status = 'processing'
            refund.save(update_fields=['provider_refund_id', 'status'])
        
        return refund
    
    @staticmethod
    @transaction.atomic
    def process_refund_succeeded(refund_id):
        """Mark refund as succeeded."""
        refund = Refund.objects.select_for_update().get(pk=refund_id)
        
        refund.status = 'succeeded'
        refund.succeeded_at = timezone.now()
        refund.save(update_fields=['status', 'succeeded_at'])
        
        
        payment = refund.payment
        total_refunded = payment.refunds.filter(
            status='succeeded'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if total_refunded >= payment.amount:
            payment.status = 'refunded'
            payment.refunded_at = timezone.now()
            payment.save(update_fields=['status', 'refunded_at'])
            
            
            transaction.on_commit(lambda: publish_to_outbox(
                event_type='RefundIssued',
                aggregate_id=payment.id,
                payload={
                    'payment_id': str(payment.id),
                    'enrollment_id': str(payment.enrollment_id),
                    'refund_amount': str(total_refunded),
                    'occurred_at': timezone.now().isoformat(),
                }
            ))
        
        return refund
```

---





```python

@dataclass(frozen=True)
class PaymentSucceededEvent:
    """
    Payment succeeded event.
    
    Consumed by:
    - Enrollment Domain (activate enrollment)
    - Notifications Domain (send receipt)
    - Analytics Domain (track revenue)
    """
    payment_id: UUID
    enrollment_id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    occurred_at: datetime
```

**Обработка:** Outbox Pattern

**Consumers:**
- `enrollment/` → activate enrollment
- `notifications/` → send receipt email
- `analytics/` → revenue tracking

---



```python

@dataclass(frozen=True)
class PaymentFailedEvent:
    payment_id: UUID
    enrollment_id: UUID
    user_id: UUID
    failure_code: str
    failure_message: str
    occurred_at: datetime
```

**Consumers:**
- `enrollment/` → suspend enrollment
- `notifications/` → notify student

---



```python

@dataclass(frozen=True)
class RefundIssuedEvent:
    payment_id: UUID
    enrollment_id: UUID
    refund_amount: Decimal
    occurred_at: datetime
```

**Consumers:**
- `enrollment/` → drop enrollment
- `notifications/` → notify student

---



| BR-ID | Rule                                                          |
|-------|---------------------------------------------------------------|
| BR-01 | Payment amount must be > 0                                    |
| BR-02 | Idempotency key prevents duplicate payments                  |
| BR-03 | Payment can only be refunded if status = 'succeeded'          |
| BR-04 | Total refund amount cannot exceed payment amount              |
| BR-05 | Webhook signature must be verified (security)                 |
| BR-06 | Failed payment → retry max 3 times                            |
| BR-07 | Payment record is immutable after terminal state              |
| BR-08 | All financial operations logged in PaymentTransaction         |

---





```python

import stripe
from django.conf import settings

class StripeClient:
    """Wrapper for Stripe API."""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, amount, currency, metadata):
        """Create payment intent."""
        intent = stripe.PaymentIntent.create(
            amount=amount,  
            currency=currency,
            metadata=metadata,
            automatic_payment_methods={'enabled': True},
        )
        return intent
    
    def create_refund(self, payment_intent_id, amount):
        """Create refund."""
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount,
        )
        return refund
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature."""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            raise ValidationError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValidationError("Invalid signature")
```



```python

import requests
import base64
from django.conf import settings

class PaymeClient:
    """Wrapper for Payme.uz API."""
    
    def __init__(self):
        self.base_url = settings.PAYME_BASE_URL
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.secret_key = settings.PAYME_SECRET_KEY
    
    def create_transaction(self, amount, order_id):
        """Create transaction."""
        payload = {
            "method": "CreateTransaction",
            "params": {
                "amount": amount * 100,  
                "account": {"order_id": order_id}
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api",
            json=payload,
            auth=(self.merchant_id, self.secret_key)
        )
        
        return response.json()
```

---





**Description:** Create payment

**Request:**
```json
{
  "enrollment_id": "uuid",
  "amount": 100.00,
  "currency": "USD",
  "payment_method": "card"
}
```

**Response:**
```json
{
  "id": "uuid",
  "client_secret": "pi_xxx_secret_xxx",
  "status": "pending",
  "amount": 100.00,
  "currency": "USD"
}
```

---



**Description:** Webhook handler for Stripe/Payme

**Security:** Signature verification required

---



**Description:** Get payment details

---



**Description:** Create refund (Admin only)

---





- ❌ **NEVER** store full card numbers
- ✅ Store only last 4 digits
- ✅ Use Stripe.js / Payme SDK (client-side tokenization)
- ✅ Payment page served over HTTPS
- ✅ CSP headers configured



```python

def verify_stripe_webhook(request):
    """Verify webhook signature."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    return event
```

---





```python

def test_create_payment_generates_idempotency_key():
    payment = PaymentProcessor.create_payment(...)
    assert payment.idempotency_key is not None
```



```python

@pytest.mark.stripe
def test_create_payment_intent():
    client = StripeClient()
    intent = client.create_payment_intent(amount=10000, currency='usd', ...)
    assert intent.id.startswith('pi_')
```

---



**Critical Metrics:**
- Payment success rate (target: >95%)
- Average payment processing time
- Failed payment reasons
- Refund rate
- Webhook processing latency

**Alerts:**
- Payment success rate < 90%
- Webhook processing > 5 seconds
- Failed webhook signature verification

---



1. **Subscriptions** — recurring monthly/yearly payments
2. **Installment plans** — split payment into 3-6 months
3. **Promo codes / Discounts**
4. **Multi-currency support** — UZS, KZT, RUB
5. **Cryptocurrency payments** — Bitcoin, USDT
6. **Invoice generation** — PDF invoices for accounting

---



- ADR-032: Enrollment Domain Extraction
- docs/ARCHITECTURE_REVISED.md
- docs/design/ENROLLMENT_DOMAIN_V1.md
- Stripe API Documentation
- Payme.uz API Documentation

---

**Last Updated:** 2026-06-08  
**Next Review:** After Phase 1B implementation
