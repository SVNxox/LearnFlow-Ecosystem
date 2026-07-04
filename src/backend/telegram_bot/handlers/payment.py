"""
Handlers for payment-related events.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery
from asgiref.sync import sync_to_async

from src.backend.payment.application.services.telegram_payment_service import TelegramPaymentService

logger = logging.getLogger(__name__)

router = Router()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    """Обработка pre_checkout_query — всегда отвечаем OK."""
    logger.info(f"✅ Pre-checkout query received: {pre_checkout_query.id}")
    logger.info(f"  User ID: {pre_checkout_query.from_user.id}")
    logger.info(f"  Invoice payload: {pre_checkout_query.invoice_payload}")
    logger.info(f"  Total amount: {pre_checkout_query.total_amount} tiyin")

    
    await pre_checkout_query.answer(ok=True)
    logger.info("✅ Pre-checkout approved")


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message) -> None:
    """Обработка успешной оплаты."""
    try:
        if not message.successful_payment:
            logger.warning("No successful_payment in message")
            return

        payment_id = message.successful_payment.invoice_payload
        total_amount = message.successful_payment.total_amount
        telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id
        provider_payment_charge_id = message.successful_payment.provider_payment_charge_id

        logger.info(f"✅ SUCCESSFUL PAYMENT RECEIVED!")
        logger.info(f"  Payment ID: {payment_id}")
        logger.info(f"  Total amount: {total_amount} tiyin ({total_amount / 100} UZS)")
        logger.info(f"  Telegram charge ID: {telegram_payment_charge_id}")
        logger.info(f"  Provider charge ID: {provider_payment_charge_id}")

        
        payment = await sync_to_async(
            TelegramPaymentService.process_successful_payment
        )(
            payment_id=payment_id,
            total_amount=total_amount,
            telegram_payment_charge_id=telegram_payment_charge_id,
            provider_payment_charge_id=provider_payment_charge_id,
        )

        await message.answer(
            text=f"✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
                 f"💰 Summa: <b>{payment.amount} {payment.currency}</b>\n\n"
                 f"Rahmat! Siz kursga muvaffaqiyatli yozildingiz.\n"
                 f"Endi kurslaringiz sahifasiga o'tib, o'qishni boshlashingiz mumkin.",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ Error in successful_payment_handler: {e}", exc_info=True)
        await message.answer(
            text="✅ To'lov qabul qilindi!\n\n"
                 "Lekin tizimda texnik xatolik yuz berdi. "
                 "Agar kursga kira olmasangiz, administrator bilan bog'laning."
        )



@router.message(lambda message: message.payment is not None and message.payment.status != 'paid')
async def failed_payment_handler(message: Message) -> None:
    """Обработка отклонённой оплаты."""
    if message.payment:
        logger.warning(f"❌ Payment failed: {message.payment.total_amount} {message.payment.currency}")
        logger.warning(f"  Status: {message.payment.status}")
        logger.warning(f"  Charge ID: {message.payment.telegram_payment_charge_id}")

        
        try:
            from src.backend.payment.domain.models import Payment
            from django.utils import timezone

            payment_id = message.payment.invoice_payload
            await sync_to_async(
                Payment.objects.filter(id=payment_id).update
            )(
                status='failed',
                failed_at=timezone.now(),
                failure_message='Payment rejected by provider'
            )
            logger.info(f"✅ Payment {payment_id} marked as failed in DB")
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")

        await message.answer(
            text="❌ <b>To'lov rad etildi</b>\n\n"
                 "Iltimos, qayta urinib ko'ring yoki boshqa to'lov usulini tanlang.\n\n"
                 "Agar muammo davom etsa, administrator bilan bog'laning.",
            parse_mode="HTML"
        )