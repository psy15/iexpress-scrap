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
    with open("myfile.id", "r") as file1:
        lines = file1.read().splitlines()
        return lines


def write_to_file(titles):
    with open("myfile.id", "a") as file1:
        # Writing data to a file
        for i in titles:
            # file1.write("Hello \n")
            file1.write(str(i)+'\n')


def get_list_of_urls():

    target_url = "https://indianexpress.com/section/explained/"
    r1 = requests.get(target_url)

    soup = BeautifulSoup(r1.content, 'html.parser')

    urls, ivs, title = [], [], []
    link = soup.find(id="north-east-data")

    for i in link.find_all('a'):
        t = i.text
        if len(t) >= 10:
            title.append(i.text)
            urls.append(i.get('href'))

    lis = read_from_file()

    for i in urls:
        ivs.append(f"http://t.me/iv?url={i}&rhash=1398b799d706ac")

    res = dict(zip(urls, title))
    for i in urls:
        if i in lis:
            res.pop(i)
        else:
            print(i)

    write_to_file(list(res))
    return res


# def start(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     update.message.reply_markdown_v2(
#         fr'Hi {user.mention_markdown_v2()}\!',
#         reply_markup=ForceReply(selective=True),
#     )


def fun():
    bot = telegram.Bot(token=TOKEN)
    dict_ = get_list_of_urls()

    message_template = "<b>{title}</b><a href='{link}'> {lin}</a>"

    for i in dict_:

        iv = f"http://t.me/iv?url={i}&rhash=1398b799d706ac"
        message = message_template.format(
            link=iv, title=dict_[i], lin="[link]")
        log.info("message: {}".format(message))
        bot.sendMessage(chat_id=CHANNEL,
                        parse_mode=telegram.ParseMode.HTML, text=message, disable_web_page_preview=False)
        sleep(120)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("start", start))

    fun()


if __name__ == '__main__':
    main()
