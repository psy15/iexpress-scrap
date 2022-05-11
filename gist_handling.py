import os
import sys
import github
import dotenv
import logging

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

GTOKEN = os.getenv('GTOKEN')
GIST_ID = os.getenv('GIST_ID')

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


def read_last_posted_url_from_gist() -> str:
    try:
        file = gist.files['ie_url'].content
        return file.strip()
    except:
        log.exception("Error reading gist!!")


def write_last_posted_url_to_gist(url: str) -> None:
    try:
        gist.edit(
            description="using for heroku",
            files={"ie_url": github.InputFileContent(content=url[0])},
        )
    except:
        log.exception("Error writing gist!!")
