import os
import github
import dotenv
from logger import log


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

GTOKEN = os.getenv('GTOKEN')
GIST_ID = os.getenv('GIST_ID')


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
            description="last posted url updated!",
            files={"ie_url": github.InputFileContent(content=url[0])},
        )
    except:
        log.exception("Error writing gist!!")
