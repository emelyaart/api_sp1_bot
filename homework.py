import os
import time

import requests
import telegram
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='w'
)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API = os.getenv('PRAKTIKUM_API')


def parse_homework_status(homework):
    homework_name = homework.get('lesson_name')
    reviewer_comment = homework.get('reviewer_comment')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, можно приступать'
                   ' к следующему уроку.')
    return (f'У вас проверили работу "{homework_name}"!\n\n{verdict}\n\n'
            f'Комментарий: {reviewer_comment}')


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': 'OAuth ' + PRAKTIKUM_TOKEN}

    homework_statuses = requests.get(API, headers=headers, params=params)
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

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message(f'Бот столкнулся с ошибкой: {e}', bot)
            time.sleep(5)


if __name__ == '__main__':
    main()
