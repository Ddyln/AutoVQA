import zipfile


def unzip_file(zip_path, extract_to):
    """
    Unzips a zip file to the specified directory.

    Args:
        zip_path (str): The path to the zip file.
        extract_to (str): The directory to extract the contents to.
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
