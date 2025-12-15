import asyncio
import json
import os
from typing import Optional

from loguru import logger

from autovqa.collect.utils.data_configs import (
    IMAGE_EXTRACTED_DESTINATION,
    TEXT_EXTRACTED_DESTINATION,
    TEXTZIP_DESTINATION,
    TEXTZIP_ID,
)
from autovqa.collect.utils.data_downloader import download_file_from_google_drive
from autovqa.collect.utils.data_utils import unzip_file
from autovqa.collect.utils.image_downloader import download_many


def data_downloader(DATA_ID, DATA_DESTINATION, FILENAME):
    """
    Downloads a file from Google Drive using its ID and
    saves it to the specified destination.

    Args:
        DATA_ID (str): The ID of the file on Google Drive.
        DATA_DESTINATION (str): The local path where the file should be saved.
    """

    # Check if the destination directory exists, if not, create it
    if not os.path.exists(DATA_DESTINATION):
        os.makedirs(DATA_DESTINATION)
        logger.info(f"Created directory: {DATA_DESTINATION}")

    destination_path = os.path.join(DATA_DESTINATION, FILENAME)

    logger.info(
        f"Downloading data from Google Drive with ID: {DATA_ID} to {destination_path}"
    )
    download_file_from_google_drive(DATA_ID, destination_path)
    logger.info("Download completed.")


def data_extraction(zip_path=None, extract_to=None):
    # check the zip_path is not exists
    if not os.path.exists(zip_path):
        logger.error(f"Zip file not found: {zip_path}")
        return

    # check the extract_to directory exists
    if os.path.exists(extract_to):
        logger.info(f"The directory {extract_to} already exists.")
    else:
        os.makedirs(extract_to)
        logger.info(f"Created directory {extract_to} for extraction.")

    unzip_file(zip_path, extract_to)
    logger.info("Data extraction completed.")


def download_image_from_urls(
    input_dir: str = TEXT_EXTRACTED_DESTINATION,
    output_dir: str = os.path.join(IMAGE_EXTRACTED_DESTINATION, "raw_images_from_urls"),
) -> None:
    """Download images whose URLs are listed in a single JSON file inside input_dir.

    The JSON file is expected to contain a list of objects each with a "url" key.
    Duplicates are removed preserving first occurrence order. Already-downloaded
    files are skipped.
    """
    files = os.listdir(input_dir)
    json_files = [file for file in files if file.endswith(".json")]
    if not json_files:
        logger.warning(f"No JSON file found in {input_dir}.")
        return
    logger.info(f"Found JSON file: {json_files[0]}")
    json_path = os.path.join(input_dir, json_files[0])

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect URLs, preserving order and deduplicating
    raw_urls: list[str] = []
    for item in data:
        url = item.get("coco_url")
        if isinstance(url, str):  # basic validation
            raw_urls.append(url)
    seen: set[str] = set()
    urls: list[str] = [u for u in raw_urls if u not in seen]
    logger.info(f"Total unique URLs: {len(urls)}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    existing_files = set(os.listdir(output_dir))
    urls_to_download: list[str] = [
        url for url in urls if url.split("/")[-1] not in existing_files
    ]
    logger.info(f"URLs to download: {len(urls_to_download)}")
    if not urls_to_download:
        logger.info("All images already downloaded.")
        return

    asyncio.run(download_many(urls_to_download, out_dir=output_dir))


def download_default_data(
    output: Optional[str] = None,
    textzip_id: str = TEXTZIP_ID,
):
    """
    Downloads and extracts the default dataset including text data and images.
    Args:
        output (Optional[str]): The base output directory. If None, defaults are used.
        textzip_id (str): The Google Drive ID for the text data zip file.
    """
    # text
    if output is not None:
        textzip_destination = os.path.join(output, "textzip")
        text_extracted_destination = os.path.join(output, "text_extracted")
        image_extracted_destination = os.path.join(output, "image_extracted")
    else:
        textzip_destination = TEXTZIP_DESTINATION
        text_extracted_destination = TEXT_EXTRACTED_DESTINATION
        image_extracted_destination = IMAGE_EXTRACTED_DESTINATION

    data_downloader(textzip_id, textzip_destination, "Data.zip")
    data_extraction(
        zip_path=os.path.join(textzip_destination, "Data.zip"),
        extract_to=text_extracted_destination,
    )

    # images
    download_image_from_urls(
        input_dir=os.path.join(text_extracted_destination, "Data", "combined_dataset"),
        output_dir=os.path.join(image_extracted_destination, "raw_images_from_urls"),
    )
