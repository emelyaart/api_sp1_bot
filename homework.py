import json
import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='w'
)

PRAKTIKUM_TOKEN = os.environ.get('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    if 'status' not in homework and 'homework_name' not in homework:
        raise KeyError('Ошибка - нет нужного ключа')
    homework_name = homework.get('homework_name')
    current_status = homework.get('status')
    status_valid = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось, '
                    'можно приступать к следующему уроку.',
        'reviewing': 'Ревьюер начал проверять вашу работу.'
    }
    verdict = status_valid.get(current_status)

    if verdict is None:
        raise Exception('Ошибка - невалидный статус')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    payload = {'from_date': current_timestamp}
    headers = {'Authorization': 'OAuth ' + PRAKTIKUM_TOKEN}

    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        headers=headers, params=payload)

    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Сообщение отправлено')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.debug('Бот запущен')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except json.JSONDecodeError:
            logging.error('Запрос содержит невалидный JSON')
            send_message('Запрос содержит невалидный JSON', bot)
            time.sleep(5)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message(f'Бот столкнулся с ошибкой: {e}', bot)
            time.sleep(5)


if __name__ == '__main__':
    main()
