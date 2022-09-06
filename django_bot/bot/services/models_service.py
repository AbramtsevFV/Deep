from asgiref.sync import sync_to_async

from bot.models import UserTg, RequestResponse, StandardMessages


async def save_and_get_user(message) -> UserTg:
    """ Сохраняет обновлять пользователя"""

    user_id = message.from_id
    username = message.from_user.username
    user, result = await UserTg.objects.aget_or_create(user_id=user_id)
    if username != user.user_name:
        await user.objects.aupdate(user_name=username)
    return user


async def save_request_response(user: UserTg, message_in: str, meessage_out: str) -> None:
    """Функция сохраняет запрос ответ от пользователя"""

    await RequestResponse.objects.acreate(user=user, request=message_in, response=meessage_out)


async def get_standard_text(command: str) -> str:
    """Функция возвращает стандартные сообщения"""
    res = await sync_to_async(StandardMessages.objects.filter)(command=command)
    if res:
        return res[0].message
    return "Бот находится в стадии наполнения БД. Мы скоро всё исправим"
