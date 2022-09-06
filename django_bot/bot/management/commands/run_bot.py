from aiogram.utils import executor
from django.core.management import BaseCommand
from bot.bot import dp

class Command(BaseCommand):
    help = 'Start bot'

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
