"""
Global configuration module for the package.

This file defines:
- Default directories for dataset storage
- Google Drive file IDs (or dataset IDs)
- Paths for ZIP files, extracted data, JSON, and preprocessed images
- A simple mechanism for user override via environment variables

All paths are resolved inside the OS-standard *user data directory*,
ensuring this library does not write files into the user's working directory.
"""

import os

from appdirs import user_data_dir

# 1. Base directory for storing all data
# ------------------------------------------------------------
# user_data_dir(package_name) creates a platform-dependent path:
#   - Windows: C:/Users/<name>/AppData/Local/your_package
#   - macOS:   ~/Library/Application Support/your_package
#   - Linux:   ~/.local/share/your_package
#
# This ensures library writes data in the correct OS-approved location.

PACKAGE_NAME = "your_package_name"

DEFAULT_BASE_DIR = user_data_dir(PACKAGE_NAME)

# Allow user override via environment variable
BASE_DESTINATION = os.environ.get("YOURPKG_BASE_DIR", DEFAULT_BASE_DIR)


# 2. Google Drive or Dataset IDs
# ------------------------------------------------------------
TEXTZIP_ID = "1hRXBHR3QAUy5XPbdyBGsge3GH9FQB4x9"
IMAGESZIP_ID = "1Dq4_2eQe_qEqWa6nMJ2S14X78QykZVBC"
RAW_IMAGESZIP_ID = "1Cj6ZX_zAZGJvL2v0eiWL4s4gG3gLvADN"


# 3. Directory layout (inside BASE_DESTINATION)
# ------------------------------------------------------------
# The folder structure used by the library.
# Normally each folder is created lazily by the functions that need it.

ZIP_DESTINATION = os.path.join(BASE_DESTINATION, "zip_files/")
TEXT_EXTRACTED_DESTINATION = os.path.join(BASE_DESTINATION, "text/")
IMAGE_EXTRACTED_DESTINATION = os.path.join(BASE_DESTINATION, "images/")


# 4. Specific target files
# ------------------------------------------------------------
# JSON dataset location
# Preprocessed image folder location

TEXT_JSON_DESTINATION = os.path.join(
    TEXT_EXTRACTED_DESTINATION, "combined_dataset.json"
)

PREPROCESSED_IMAGE_DESTINATION = os.path.join(
    IMAGE_EXTRACTED_DESTINATION, "preprocessed/"
)


# 5. Utility: ensure directory exists (optional)
# ------------------------------------------------------------
# This function can be used by your pipeline to guarantee that
# required directories are created before saving files.
def ensure_directories():
    """Create required directories if they do not already exist."""
    for d in [
        BASE_DESTINATION,
        ZIP_DESTINATION,
        TEXT_EXTRACTED_DESTINATION,
        IMAGE_EXTRACTED_DESTINATION,
        PREPROCESSED_IMAGE_DESTINATION,
    ]:
        os.makedirs(d, exist_ok=True)
