"""
Management command to run Telegram bot.

Usage:
    python manage.py run_bot
"""

import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **options):
        """Запускает Telegram бота."""
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not configured in settings')
            )
            return

        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))

        from src.backend.telegram_bot.bot import initialize

        bot, dp = initialize()

        self.stdout.write(self.style.SUCCESS('Bot initialized. Starting polling...'))

        try:
            asyncio.run(self._run_polling(bot, dp))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Bot stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            logger.error(f"Error running bot: {e}", exc_info=True)

    async def _run_polling(self, bot, dp):
        """Запускает polling."""
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)