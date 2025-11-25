import cv2
import numpy as np


def denoise_image(image: np.ndarray) -> np.ndarray:
    """
    Apply noise reduction to a color image using OpenCV's
    fast Non-local Means Denoising algorithm.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format with shape (H, W, 3) and dtype uint8.

    Returns
    -------
    np.ndarray
        Denoised image in BGR format with the same shape and dtype as input.

    Raises
    ------
    ValueError
        If the input is not a 3-channel BGR image.

    Notes
    -----
    - Uses `cv2.fastNlMeansDenoisingColored` with default parameters:
        - h=3, hColor=3
        - templateWindowSize=7, searchWindowSize=21
    - This function does not modify the input image in-place.
    """
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Input must be a 3-channel BGR image.")

    # Placeholder for noise reduction logic
    denoised_image = cv2.fastNlMeansDenoisingColored(
        image, dst=None, h=3, hColor=3, templateWindowSize=7, searchWindowSize=21
    )
    return denoised_image
