import os
from typing import Tuple

import cv2
import numpy as np

from autovqa.config.config import IMAGE_EXTRACTED_DESTINATION
from autovqa.preprocess.image.color_correction import color_correction
from autovqa.preprocess.image.denoise import denoise_image
from autovqa.preprocess.image.find_common_size import find_most_common_image_size
from autovqa.preprocess.image.normalize import normalize_image  # Optional
from autovqa.preprocess.image.resize import pad_image, resize_image
from autovqa.preprocess.image.sharpening import unsharp_mask


# ------------------ Core preprocessing function ------------------
def preprocess_image(
    image_path: str,
    target_size: Tuple[int, int] = (480, 640),
    do_normalize: bool = False,
) -> np.ndarray:
    """
    Preprocess a single image through resizing, padding, denoising,
    color correction, sharpening, and optional normalization.

    Parameters
    ----------
    image_path : str
        Path to the input image file.
    target_size : Tuple[int, int], optional
        Final expected size (height, width). Default is (480, 640).
    do_normalize : bool, optional
        Whether to apply normalization at the end. Default is False.

    Returns
    -------
    np.ndarray
        The preprocessed image in BGR format.

    Raises
    ------
    ValueError
        If the input image cannot be read.
    """
    # Load image (BGR format)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read: {image_path}")

    # Resize image while keeping aspect ratio
    resized = resize_image(image, target_size)

    # Pad image to exactly match target_size
    padded = pad_image(resized, target_size)

    # Reduce noise
    denoised = denoise_image(padded)

    # Improve contrast using CLAHE on LAB L-channel
    corrected = color_correction(denoised)

    # Apply sharpening
    sharpened = unsharp_mask(corrected)

    # Optional normalization
    if do_normalize:
        processed = normalize_image(sharpened)
    else:
        processed = sharpened

    return processed


# ------------------ Pipeline function ------------------
def run_pipeline(
    input_folder: str = os.path.join(
        IMAGE_EXTRACTED_DESTINATION, "raw_images_from_urls"
    ),
    output_folder: str = os.path.join(
        IMAGE_EXTRACTED_DESTINATION, "preprocessed_url_images/"
    ),
    do_normalize: bool = False,
):
    """
    Run the full preprocessing pipeline on all images inside the input directory.

    This function performs batch preprocessing of images by:
    - Determining the most common image size in the input folder
    (defaulting to (480, 640) if none found).
    - Iterating through all image files (.png, .jpg, .jpeg).
    - Preprocessing each image using `preprocess_image()`.
    - Optionally normalizing image data back to 0–1
    (if `do_normalize=True`, output is converted back to 0–255 before saving).
    - Saving processed images to the output folder.

    Parameters
    ----------
    input_folder : str, optional
        Path to the directory containing raw input images.
        Default = IMAGE_EXTRACTED_DESTINATION/raw_images_from_urls.

    output_folder : str, optional
        Path to the directory where preprocessed images will be saved.
        The directory will be created if it does not exist.

    do_normalize : bool, optional
        If True, the preprocessing step will output normalized images (0–1),
        which are then rescaled to 0–255 before writing to disk.

    Notes
    -----
    - Images that already exist in the output directory are skipped.
    - Errors during image processing are caught and printed.
    - The function prints progress and status messages during execution.

    Returns
    -------
    None
        The function writes processed images to disk but does not return anything.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Determine target size
    target_size = find_most_common_image_size(input_folder, extension=".jpg") or (
        480,
        640,
    )
    print(f"Using target size: {target_size}")

    # List images
    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    print(f"Found {len(image_files)} images in {input_folder}")

    for idx, filename in enumerate(sorted(image_files)):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        if os.path.exists(output_path):
            print(f"[INFO] {output_path} already exists, skipping...")
            continue

        print(f"Processing {idx + 1}/{len(image_files)}: {filename}")
        try:
            processed_img = preprocess_image(input_path, target_size, do_normalize)
            if do_normalize:
                processed_img = (processed_img * 255).astype("uint8")
            cv2.imwrite(output_path, processed_img)
            print(f"Finished: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")


# ------------------ CLI entry ------------------
def cli():
    run_pipeline()


if __name__ == "__main__":
    cli()
