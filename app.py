import os
import logging
import sys
from time import sleep
import telegram
# from telegram import Update, ForceReply
# from telegram.ext import Updater
import requests
from bs4 import BeautifulSoup
import dotenv
import github

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

TOKEN = os.getenv('TOKEN')
CHANNEL = os.getenv('CHANNEL')
GTOKEN = os.getenv('GTOKEN')
PORT = int(os.environ.get('PORT', 5000))
GIST_ID = os.getenv('GIST_ID')
TARGET_URL = os.getenv('TARGET_URL')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s- %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

gh = github.Github(GTOKEN)
gist = gh.get_gist(GIST_ID)


def read_last_posted_url():
    try:
        file = gist.files['ie_url'].content
        return file.strip()
    except:
        log.exception("Error reading url file")


def write_last_posted_url(url):
    try:
        gist.edit(
            description="using for heroku",
            files={"ie_url": github.InputFileContent(content=url[0])},
        )
    except:
        log.exception("Error writing url file")


def get_list_of_urls():

    response = requests.get(TARGET_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    all_urls, title = [], []

    # get featured headline
    headline = soup.find("div", {"class": "northeast-topbox"})
    for i in headline.find_all('a'):
        title.append(i.text)
        all_urls.append(i.get('href'))

    # rest of the news
    data = soup.find(id="north-east-data")
    for i in data.find_all('a'):
        title_length = len(i.text)
        if title_length >= 10:
            title.append(i.text)
            all_urls.append(i.get('href'))

    last_url = str(read_last_posted_url())

    urls_to_post = {}

    for i, j in enumerate(all_urls):
        if j != last_url:
            urls_to_post[j] = [title[i]]
        else:
            break

    # get tags
    for i in urls_to_post:
        response = requests.get(i)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find("div", {"class": "storytags ev-meter-content"})

        tags = ""
        # if no tags
        if data is None:
            urls_to_post[i].append('')
            continue

        #make tag lowercase and prepend with #
        for j in data.find_all('a'):
            tags += ' #' + j.text.lower().replace(' ', '_').replace('-', '_')

        urls_to_post[i].append(tags[1:])

    # cwrite to file heck if dictionary if empty
    if bool(urls_to_post):
        write_last_posted_url(list(urls_to_post)[:1])
        return urls_to_post

    log.info('no new posts found..')
    exit()  # exit if empty


def post():
    bot = telegram.Bot(token=TOKEN)
    dict_ = get_list_of_urls()

    message_template = "<b>{title}</b><a href='{link}'> {text}</a> \n{tags}"

    for i in reversed(dict_):

        iv = f"http://t.me/iv?url={i}&rhash=1398b799d706ac"

        # dict[i][0] is url, dict[i][1] is tag string
        message = message_template.format(
            link=iv, title=dict_[i][0], text="[link]", tags=dict_[i][1])
        log.info(f"posting message: {message}")
        bot.sendMessage(chat_id=CHANNEL,
                        parse_mode=telegram.ParseMode.HTML, text=message,
                        disable_web_page_preview=False)

        # if last message then break, break without delay
        if i == list(dict_)[0]:
            break

        sleep(180)


def main() -> None:

    post()


if __name__ == '__main__':
    main()
