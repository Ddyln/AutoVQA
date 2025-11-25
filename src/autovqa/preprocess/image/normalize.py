from typing import List

import numpy as np


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize pixel values of a single image to the range [0, 1].

    Parameters
    ----------
    image : np.ndarray
        Input image array in any numeric dtype (e.g., uint8) with shape
        (H, W, C) for color images or (H, W) for grayscale.

    Returns
    -------
    np.ndarray
        Normalized image as float32 with values in [0, 1]
        and same shape as input.

    Notes
    -----
    - The input image is converted to float32 automatically.
    - Does not modify the input array in-place.
    """
    # Ensure the image is in float format
    image = image.astype("float32")

    # Normalize the image
    normalized_image = image / 255.0

    return normalized_image


def normalize_batch(images: List[np.ndarray]) -> List[np.ndarray]:
    """
    Normalize a batch of images to the range [0, 1].

    Parameters
    ----------
    images : List[np.ndarray]
        List of input image arrays.

    Returns
    -------
    List[np.ndarray]
        List of normalized images in float32 format with values in [0, 1].

    Notes
    -----
    - Uses `normalize_image` internally for each image.
    - Input images are not modified in-place.
    """
    return [normalize_image(image) for image in images]
