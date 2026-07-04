"""
Handler for /start command with payment parameter.
"""

import logging
import asyncio
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, LabeledPrice
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.exceptions import TelegramBadRequest

from src.backend.payment.domain.models import Payment

logger = logging.getLogger(__name__)

router = Router()


MIN_AMOUNT_TIYIN = 10000


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Обработка команды /start с параметром pay_PAYMENT_ID."""
    try:
        
        args = message.text.split()
        if len(args) < 2 or not args[1].startswith('pay_'):
            await message.answer(
                "Assalomu alaykum! 👋\n\n"
                "Bu bot LearnFlow platformasi uchun to'lovlar qabul qiladi.\n\n"
                "To'lov qilish uchun saytdan to'lov tugmasini bosing."
            )
            return

        payment_id = args[1].replace('pay_', '')

        
        payment: Payment = await sync_to_async(
            Payment.objects.get
        )(id=payment_id)

        
        if payment.status in ['succeeded', 'failed', 'cancelled', 'refunded']:
            status_messages = {
                'succeeded': "✅ Bu to'lov allaqachon muvaffaqiyatli amalga oshirilgan.",
                'failed': "❌ Bu to'lov amalga oshmagan.",
                'cancelled': "❌ Bu to'lov bekor qilingan.",
                'refunded': "💰 Bu to'lov uchun pul qaytarilgan.",
            }
            await message.answer(status_messages.get(payment.status, "To'lov holati noma'lum."))
            return

        
        course_title = "Kurs"
        if payment.enrollment_id:
            from src.backend.enrollment.domain.models import CourseEnrollment
            from src.backend.learning.domain.models import Course
            try:
                enrollment = await sync_to_async(CourseEnrollment.objects.get)(
                    id=payment.enrollment_id
                )
                course = await sync_to_async(Course.objects.get)(
                    id=enrollment.course_id
                )
                course_title = course.title
            except Exception as e:
                logger.error(f"Error fetching course: {e}")

        
        amount_in_uzs = float(payment.amount)
        amount_in_tiyin = int(amount_in_uzs * 100)

        
        if amount_in_tiyin < MIN_AMOUNT_TIYIN:
            await message.answer(
                f"❌ To'lov summasi juda kam.\n\n"
                f"Joriy summa: {amount_in_uzs:.2f} UZS\n"
                f"Minimal summa: {MIN_AMOUNT_TIYIN // 100} UZS"
            )
            return

        
        CLICK_TOKEN = settings.CLICK_PROVIDER_TOKEN
        if not CLICK_TOKEN:
            await message.answer(
                "❌ To'lov tizimi sozlanmagan.\n\n"
                "Iltimos, administrator bilan bog'laning."
            )
            logger.error("CLICK_PROVIDER_TOKEN not configured")
            return

        
        prices = [
            LabeledPrice(
                label=f"Kurs: {course_title}",
                amount=amount_in_tiyin
            )
        ]

        try:
            
            await message.answer_invoice(
                title="LearnFlow",
                description=f"{course_title} kursi uchun to'lov",
                payload=str(payment.id),
                currency="UZS",
                provider_token=CLICK_TOKEN,
                prices=prices,
                start_parameter=f"pay_{payment.id}",
                need_phone_number=True,
                need_name=False,
                need_email=False,
                need_shipping_address=False,
            )

            logger.info(f"✅ Invoice created successfully for payment {payment_id}")

            
            await message.answer(
                "💳 <b>TEST REJIMI — To'lov ma'lumotlari:</b>\n\n"
                "<b>Karta raqami:</b> <code>8600 4905 1873 5015</code>\n"
                "<b>Muddat:</b> <code>12/26</code>\n"
                "<b>CVV:</b> <code>123</code>\n"
                "<b>SMS kod:</b> <code>666666</code>\n\n"
                "⚠️ <i>Haqiqiy pul yechilmaydi! Bu test rejimi.</i>\n\n"
                "To'lov holati avtomatik tekshiriladi...",
                parse_mode="HTML"
            )

            
            asyncio.create_task(
                poll_payment_status(message, payment_id, timeout=180)
            )

        except TelegramBadRequest as e:
            logger.error(f"Telegram API error: {e}")

            error_message = str(e).lower()

            if "currency_total_amount_invalid" in error_message:
                await message.answer(
                    f"❌ Xatolik: Noto'g'ri summa.\n\n"
                    f"Summa: {amount_in_uzs} UZS\n"
                    f"Minimal summa: {MIN_AMOUNT_TIYIN // 100} UZS"
                )
            elif "provider_token_invalid" in error_message:
                await message.answer(
                    "❌ Xatolik: To'lov tizimi sozlanmagan.\n\n"
                    "Iltimos, CLICK_PROVIDER_TOKEN ni tekshiring."
                )
            else:
                await message.answer(
                    f"❌ Xatolik yuz berdi.\n\n"
                    f"Texnik ma'lumot: {str(e)}"
                )

    except Payment.DoesNotExist:
        await message.answer("❌ To'lov topilmadi. Iltimos, qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"Error in command_start_handler: {e}", exc_info=True)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )


async def poll_payment_status(message: Message, payment_id: str, timeout: int = 60):
    """
    Polling для проверки статуса платежа.
    Если через timeout секунд статус не изменился — показываем ошибку.
    """
    logger.info(f"🔍 Starting payment status polling for {payment_id} (timeout: {timeout}s)")

    elapsed = 0
    interval = 5  
    last_status = None

    while elapsed < timeout:
        await asyncio.sleep(interval)
        elapsed += interval

        try:
            
            payment: Payment = await sync_to_async(
                Payment.objects.get
            )(id=payment_id)

            
            if payment.status != last_status:
                logger.info(f"  [{elapsed}s] Payment status changed: {last_status} → {payment.status}")
                last_status = payment.status

            
            if payment.status == 'succeeded':
                await message.answer(
                    text=f"✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
                         f"💰 Summa: <b>{payment.amount} {payment.currency}</b>\n\n"
                         f"Rahmat! Siz kursga muvaffaqiyatli yozildingiz.",
                    parse_mode="HTML"
                )
                logger.info(f"✅ Payment {payment_id} succeeded (detected by polling)")
                return

            
            elif payment.status == 'failed':
                await message.answer(
                    text="❌ <b>To'lov rad etildi</b>\n\n"
                         "Iltimos, qayta urinib ko'ring.",
                    parse_mode="HTML"
                )
                logger.info(f"❌ Payment {payment_id} failed (detected by polling)")
                return

        except Payment.DoesNotExist:
            logger.error(f"  Payment {payment_id} not found")
            return
        except Exception as e:
            logger.error(f"  Error checking payment status: {e}")

    
    logger.warning(f"⚠️ Payment polling timeout for {payment_id} (status: {last_status})")

    
    try:
        await sync_to_async(
            Payment.objects.filter(id=payment_id).update
        )(
            status='failed',
            failure_message='Payment timeout - no response from provider'
        )
        logger.info(f"✅ Payment {payment_id} marked as failed (timeout)")
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")

    
    await message.answer(
        text="❌ <b>To'lov amalga oshmadi</b>\n\n"
             "To'lov tizimi javob bermadi.\n\n"
             "<b>Sabablari:</b>\n"
             "• Click tizimida xatolik\n"
             "• Karta ma'lumotlari noto'g'ri\n"
             "• SMS kod yuborilmadi\n\n"
             "<b>Yechimlar:</b>\n"
             "1. Qayta urinib ko'ring\n"
             "2. Boshqa to'lov usulini tanlang\n"
             "3. Administrator bilan bog'laning",
        parse_mode="HTML"
    )