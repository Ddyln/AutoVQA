import cv2
import numpy as np


def color_correction(image: np.ndarray) -> np.ndarray:
    """
    Enhance image contrast using CLAHE on the L-channel in LAB color space.

    This function converts the input BGR image into LAB color space,
    applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
    to the L (lightness) channel to improve local contrast, and then
    converts the processed image back to BGR format.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format with shape (H, W, 3)
        and dtype uint8.

    Returns
    -------
    np.ndarray
        Contrast-enhanced image in BGR format with the same shape
        and dtype as the input.
    """
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Input must be a 3-channel BGR image.")

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)

    lab_eq = cv2.merge((l_eq, a, b))
    img_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
    return img_eq
