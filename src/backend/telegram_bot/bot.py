"""
Telegram Bot initialization.
"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

logger = logging.getLogger(__name__)


def get_bot() -> Bot:
    """Создаёт и возвращает экземпляр бота."""
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def get_dispatcher() -> Dispatcher:
    """Создаёт и настраивает Dispatcher."""
    from .handlers import start, payment

    dp = Dispatcher()

    
    dp.include_router(start.router)
    dp.include_router(payment.router)

    return dp



bot = None
dp = None


def initialize():
    """Инициализирует бота и диспетчер."""
    global bot, dp
    bot = get_bot()
    dp = get_dispatcher()
    logger.info("Telegram bot initialized successfully")
    return bot, dp