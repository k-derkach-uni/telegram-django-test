import asyncio
from django.core.management.base import BaseCommand
from bot.handlers import bot


class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):
        bot.polling()
