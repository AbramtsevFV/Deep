from bot.services.request_to_deep import post_to_services
import aiogram.utils.markdown as fmt


def get_text(good_words_list: list, bad_words_list: list) -> str:
    """Возвращает сообщения для пользователя"""
    check_word = lambda lst: " ".join(lst) if lst else "Отсутствуют"
    result = fmt.text(
        fmt.text(fmt.hunderline('Ругательные слова:'), fmt.hbold(check_word(bad_words_list))),
        fmt.text(fmt.hunderline('Хорошие слова:'), fmt.hbold(check_word(good_words_list))),
    )
    return result


def get_error_text() -> str:
    """Возвращает сообщения для пользователя при ошибках ответа сервиса"""
    result = fmt.text(
        fmt.text(fmt.hunderline('Повторите Ваш запрос'), ":)"),
    )
    return result


async def get_message(message):
    """Возвращает сообщени для отправки"""
    text_list = message.split(',')
    response_dict = {"sentences": text_list}
    result = await post_to_services('badlisted_words', response_dict)
    if result:
        good_words_list = []
        bad_words_list = []
        for indx, word in enumerate(text_list):
            if result[indx].get('bad_words'):
                bad_words_list.append(word)
            else:
                good_words_list.append(word)

        return get_text(good_words_list, bad_words_list)

    return get_error_text()
