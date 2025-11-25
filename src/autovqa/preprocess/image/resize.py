from typing import Tuple

import cv2
import numpy as np


def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize the input image to fit within the target size while maintaining
    the original aspect ratio.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format with shape (H, W, C) or grayscale (H, W).
    target_size : Tuple[int, int]
        Desired size as (height, width).

    Returns
    -------
    np.ndarray
        Resized image, keeping the aspect ratio. The image may be smaller
        than target_size in one dimension.

    Notes
    -----
    - This function only resizes; it does not pad the image.
    - Use `pad_image` afterwards to match exact target_size if needed.
    """
    old_size = image.shape[:2]  # (height, width)
    ratio = min(target_size[0] / old_size[0], target_size[1] / old_size[1])

    # (width, height)
    new_size = (int(old_size[1] * ratio), int(old_size[0] * ratio))

    # Resize
    resized_image = cv2.resize(image, new_size)
    return resized_image


def pad_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Pad the input image to exactly match the target size.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format with shape (H, W, C) or grayscale (H, W).
    target_size : Tuple[int, int]
        Desired size as (height, width).

    Returns
    -------
    np.ndarray
        Padded image with size exactly equal to target_size. Padding is
        applied evenly on all sides, and empty areas are filled with black.

    Notes
    -----
    - If the image is already equal to target_size, no padding is applied.
    """
    # Get the current size of the image
    current_size = image.shape[:2]  # (height, width)
    # Get the padding amounts
    delta_w = target_size[1] - current_size[1]
    delta_h = target_size[0] - current_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    # Add padding
    color = [0, 0, 0]  # Black
    padded_image = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )

    return padded_image
