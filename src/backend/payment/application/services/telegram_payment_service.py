"""
TelegramPaymentService — сервис для работы с Telegram Payments.
"""

import logging
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from src.backend.payment.domain.models import Payment

logger = logging.getLogger(__name__)


class TelegramPaymentService:
    """Сервис для работы с Telegram Payments."""

    @staticmethod
    def create_invoice_url(payment_id: UUID, bot_username: str) -> str:
        """
        Создаёт URL для оплаты через Telegram.

        Args:
            payment_id: UUID платежа
            bot_username: Username бота (без @)

        Returns:
            URL для оплаты через Telegram
        """
        
        return f"https://t.me/{bot_username}?start=pay_{payment_id}"

    @staticmethod
    def process_successful_payment(
            payment_id: str,
            total_amount: int,
            telegram_payment_charge_id: Optional[str] = None,
            provider_payment_charge_id: Optional[str] = None,
    ) -> Payment:
        """
        Обрабатывает успешную оплату через Telegram.

        Args:
            payment_id: ID платежа (из invoice_payload)
            total_amount: Сумма в тийинах (100 тийинов = 1 UZS)
            telegram_payment_charge_id: ID платежа от Telegram
            provider_payment_charge_id: ID платежа от провайдера

        Returns:
            Обновлённый Payment
        """
        from src.backend.payment.domain.services.payment_processor import PaymentProcessor

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            raise ValueError(f"Payment {payment_id} not found")

        
        if payment.status in ['succeeded', 'failed', 'cancelled', 'refunded']:
            logger.warning(f"Payment {payment_id} already in terminal status: {payment.status}")
            return payment

        
        amount_uzs = total_amount / 100

        
        if abs(float(payment.amount) - amount_uzs) > 0.01:
            logger.error(
                f"Amount mismatch for payment {payment_id}: "
                f"expected {payment.amount}, got {amount_uzs}"
            )
            raise ValueError("Amount mismatch")

        
        payment.status = Payment.Status.SUCCEEDED
        payment.succeeded_at = timezone.now()
        payment.provider_payment_id = telegram_payment_charge_id or provider_payment_charge_id
        payment.metadata = {
            **payment.metadata,
            'telegram_payment_charge_id': telegram_payment_charge_id,
            'provider_payment_charge_id': provider_payment_charge_id,
            'payment_source': 'telegram',
        }
        payment.save()

        
        if payment.enrollment_id:
            from src.backend.enrollment.domain.models import CourseEnrollment
            try:
                enrollment = CourseEnrollment.objects.get(id=payment.enrollment_id)
                if enrollment.status in ['pending', 'inactive']:
                    enrollment.status = 'active'
                    enrollment.payment_status = 'paid'
                    enrollment.save(update_fields=['status', 'payment_status'])
                    logger.info(f"Enrollment {enrollment.id} activated via Telegram payment")
            except CourseEnrollment.DoesNotExist:
                logger.error(f"Enrollment {payment.enrollment_id} not found")

        logger.info(f"Payment {payment_id} successfully processed via Telegram")
        return payment