# Telegramm Bot BadWords

## Настройки
1) Заполнить env, в папке бота:
````
POSTGRES_DB=имя базы данных ( по умолчанию ставить postgres)
POSTGRES_USER=имя пользователя ( по умолчанию ставить postgres)
POSTGRES_PASSWORD=имя пароль ( по умолчанию ставить postgres)
BASE_URL= (url приложения badlisted-words)
API_TOKEN='токен бота'
````
2) Установить [Ngrok](https://ngrok.com/). Выполнить в терминале команду `ngrok http 8018` и полученный url вставить в env.

3) Команда запуска:
````
sudo docker-compose -f docker-compose.yml -f assistant_dists/dream/docker-compose.override.yml -f assistant_dists/dream/dev.yml up  badlisted-words spacy-nounphrases db web tg_bot --build
````
4) После запуска, создать администратора Django, в терминале выполнить команды 
- `docker exec -it id контейнера с DJANGO bash`
- `cd django_bot/`
- `source venvnew/bin/activate`
- `python manage.py createsuperuser`
5) Перейти в [админ панели в таблицу "Стандартное сообщение"](http://0.0.0.0:8000/admin/bot/standardmessages/). Добавить поля:
- Команда бота: start
- Текст для пользователя: ⚡️ ⚡️ ⚡️ ⚡️
Вас приветствует Telegram Bot Плохих слов на Английском!
Напишите слова или предложения через запятую. 
Запятая считается новым словосочетанием.
Слова на Русском считаются автоматом как хорошие!!!
✅✅✅✅✅✅
6) Бот запущен и готов к работе.

