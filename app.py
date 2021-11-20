import requests
from bs4 import BeautifulSoup
import os
import logging
import sys
import telegram
# from telegram import Update, ForceReply
from telegram.ext import Updater
from time import sleep
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

TOKEN = os.getenv('TOKEN')
CHANNEL = os.getenv('CHANNEL')
PORT = int(os.environ.get('PORT', 5000))

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s- %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def read_from_file():
    with open("last_posted_url.id", "r") as file1:
        return file1.read().splitlines()


def write_to_file(url):
    with open("last_posted_url.id", "w") as file1:
        file1.write(str(url[0]))


def get_list_of_urls():

    target_url = "https://indianexpress.com/section/explained/"
    response = requests.get(target_url)

    soup = BeautifulSoup(response.content, 'html.parser')

    all_urls, title = [], []

    headline = soup.find("div", {"class": "northeast-topbox"})
    for i in headline.find_all('a'):
        title.append(i.text)
        all_urls.append(i.get('href'))

    link = soup.find(id="north-east-data")
    for i in link.find_all('a'):
        title_length = len(i.text)
        if title_length >= 10:
            title.append(i.text)
            all_urls.append(i.get('href'))

    last_url = str(read_from_file()[0])

    urls_to_post = {}

    for i in range(len(all_urls)):
        if all_urls[i] != last_url:
            urls_to_post[all_urls[i]] = title[i]
        else:
            break

    if bool(urls_to_post):
        write_to_file(list(urls_to_post)[:1])

    return urls_to_post


def fun():
    bot = telegram.Bot(token=TOKEN)
    dict_ = get_list_of_urls()

    message_template = "<b>{title}</b><a href='{link}'> {lin}</a>"

    for i in reversed(dict_):

        iv = f"http://t.me/iv?url={i}&rhash=1398b799d706ac"
        message = message_template.format(
            link=iv, title=dict_[i], lin="[link]")
        log.info("message: {}".format(message))
        bot.sendMessage(chat_id=CHANNEL,
                        parse_mode=telegram.ParseMode.HTML, text=message, disable_web_page_preview=False)
        sleep(180)


def main() -> None:

    while True:
        fun()
        sleep(7200)


if __name__ == '__main__':
    main()
