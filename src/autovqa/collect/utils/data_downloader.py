import gdown
from loguru import logger


def download_file_from_google_drive(id, destination):
    try:
        gdown.download(id=id, output=destination, quiet=False)
    except Exception as e:
        logger.info(f"[FAILED] Can't download file from Google Drive. ERROR: {e}")
        raise e
