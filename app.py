import os
import sys
from time import sleep
import telegram
# from telegram import Update, ForceReply
# from telegram.ext import Updater
import requests
from bs4 import BeautifulSoup
import dotenv
from logger import log

from gist_handling import read_last_posted_url_from_gist, write_last_posted_url_to_gist

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

TOKEN = os.environ['TOKEN']
CHANNEL = os.environ['CHANNEL']
PORT = os.environ['PORT']
TARGET_URL = os.environ['TARGET_URL']


def map_url_to_title(hyperlinks, urls_to_post, last_url):

    for hyperlink in hyperlinks:
        title = hyperlink.text
        title_length = len(title)
        url = hyperlink.get('href')

        # validation
        if title_length >= 10:
            if url != last_url:
                urls_to_post[url] = [title]
            else:
                return False

    return True  # if new posts found


def get_list_of_urls() -> dict:

    response = requests.get(TARGET_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    last_url = read_last_posted_url_from_gist()
    urls_to_post = {}

    # get featured headline
    headline = soup.find("div", {"class": "northeast-topbox"})

    # if new posts found
    if map_url_to_title(headline.find_all('a'), urls_to_post, last_url):
        # rest of the posts
        data = soup.find(id="north-east-data")
        map_url_to_title(data.find_all('a')[:10], urls_to_post, last_url)

    # get tags
    for url in urls_to_post:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find("div", {"class": "storytags ev-meter-content"})

        tags = ""
        # if no tags
        if data is None:
            urls_to_post[url].append('')
            continue

        # make tag lowercase, replace spaces and '-' with '_' and prepend str with #
        for tag in data.find_all('a'):
            tags += f" #{tag.text.lower().replace(' ', '_').replace('-', '_')}"

        urls_to_post[url].append(tags.lstrip())

    # write to file if dictionary is not empty
    if bool(urls_to_post):
        write_last_posted_url_to_gist(list(urls_to_post)[:1])
        return urls_to_post

    log.info('no new posts found..')
    sys.exit()  # exit if empty


# post message to channel
def post() -> None:
    bot = telegram.Bot(token=TOKEN)
    mapped_urls = get_list_of_urls()
    # mapped_urls : { url: [title,tags]}

    message_template = "<b>{title}</b><a href='{link}'> {text}</a> \n{tags}"

    for url, (title, tags) in reversed(mapped_urls.items()):

        # iv_url = f"http://t.me/iv?url={url}&rhash=1398b799d706ac"
        iv_url = url

        message = message_template.format(
            link=iv_url,
            title=title,
            text="🔗",
            tags=tags
        )

        log.info("posting message: %s", message)

        bot.sendMessage(
            chat_id=CHANNEL,
            parse_mode=telegram.ParseMode.HTML,
            text=message,
            disable_web_page_preview=False
        )

        # if last message then break, break without delay
        if url == list(mapped_urls)[0]:
            break

        sleep(180)


def main() -> None:
    post()


if __name__ == '__main__':
    main()
