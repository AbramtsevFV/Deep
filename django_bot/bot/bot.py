import logging

from aiogram import Bot, Dispatcher, executor, types
from bot.models import UserTg

from bot.services.models_service import save_and_get_user, save_request_response, get_standard_text
from bot.services.parser import get_message

API_TOKEN = '5426020191:AAFohIi1LmlC-zDftsYAj7udfbyJUJDeA58'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def get_model():
    return UserTg.objects.all()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    text = await get_standard_text('start')
    await message.reply(text)


@dp.message_handler()
async def echo(message: types.Message):
    user = await save_and_get_user(message)
    text = message.text
    if text:
        message_for_send = await get_message(text)
        await save_request_response(user, text, message_for_send)
        await message.answer(message_for_send, parse_mode="HTML")
    else:
        await message.answer("Собщение не должно быть пустым")
