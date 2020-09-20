import logging
import os
import time

import requests
import telegram

from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(filename="sample.log", level=logging.INFO)
log = logging.getLogger("ex")

PROXY = 'socks5://167.71.203.212:1080'

URL_API = 'https://praktikum.yandex.ru/api/user_api'
METHOD_API = 'homework_statuses'

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

proxy_server = telegram.utils.request.Request(proxy_url=PROXY)
bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy_server)

STATUS = {'approved': 'Ревьюеру всё понравилось, '
                      'можно приступать к следующему уроку.',
          'rejected': 'К сожалению в работе нашлись ошибки.'}


def parse_homework_status(homework):
    """check status homework"""
    if not homework.get('homework_name'):
        log.error(f'An error occurred while requesting a name value!')
        return f'An error occurred while requesting a name value!'
    homework_name = homework.get('homework_name')

    if not homework.get('status'):
        log.error(f'An error occured while requesting a status value!')
        return f'An error occured while requesting a status value!'
    homework_status = homework.get('status')

    if homework_status not in STATUS:
        log.error(f'Sorry! Job status request failed!')
        return f'Sorry! Job status request failed!'

    if homework_status == 'rejected':
        verdict = STATUS['rejected']
    else:
        verdict = STATUS['approved']
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """get status homework"""
    if current_timestamp is None:
        log.error(f'Error current timestamp!')
        return {}

    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(f'{URL_API}/{METHOD_API}/',
            headers=headers,
            params=params)
        # return homework status
        return homework_statuses.json()

    except requests.exceptions.RequestException as e:
        log.error(f'Connection error: {e}')
        # return homework status on error
        return {}


def send_message(message):
    """send message"""
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    """main"""
    # initial timestamp value
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            # update timestamp
            current_timestamp = new_homework.get('current_date')
            # poll every 20 minutes
            time.sleep(1200)

        except Exception as e:
            log.error(f'Bot crashed with an error: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
