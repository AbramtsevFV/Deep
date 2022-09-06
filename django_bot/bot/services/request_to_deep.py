import httpx

from django_bot.settings import BASE_URL


async def post_to_services(path: str, json: dict) -> [dict, bool]:
    """Функция возвращает ответ от сервиса"""
    url = BASE_URL + path
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json)
        if response.status_code == 200:
            return response.json()
        return False

