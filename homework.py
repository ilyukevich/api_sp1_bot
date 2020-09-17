import os, requests, telegram, time, logging
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


def parse_homework_status(homework):
    """check status homework"""
    homework_name = homework['homework_name']
    lesson_name = homework['lesson_name']
    reviewer_comment = homework['reviewer_comment']

    if reviewer_comment == '':
        comment = "no comments"
    else:
        comment = reviewer_comment

    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'

    return f'У вас проверили работу "{homework_name}"! ' \
           f'\n По уроку: "{lesson_name}". ' \
           f'\n С комментариями: "{comment}" ' \
           f'\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """get status homework"""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    #params = {'from_date': current_timestamp}
    params = {'from_date': 0}
    try:
        homework_statuses = requests.get(f'{URL_API}/{METHOD_API}/',
            headers=headers,
            params=params)
    except (requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        log.error(f'Connection error: {e}')
        print(f'Connection error: {e}')

    # returning the user's status homework
    return homework_statuses.json()


def send_message(message):
    """send message"""
    bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy_server)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    # initial timestamp value
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[3]))
            # update timestamp
            current_timestamp = new_homework.get('current_date')
            # poll every 20 minutes
            time.sleep(1200)

        except Exception as e:
            print(f'Bot crashed with an error: {e}')
            log.error(f'Bot crashed with an error: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
