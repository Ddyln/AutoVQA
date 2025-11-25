import cv2
import numpy as np


def unsharp_mask(image: np.ndarray, amount: float = 1.5) -> np.ndarray:
    """
    Sharpen an image using the Unsharp Mask technique.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format with shape (H, W, C) or grayscale (H, W).
    amount : float, optional
        Strength of sharpening. Default is 1.5. Higher values increase contrast
        at edges.

    Returns
    -------
    np.ndarray
        Sharpened image with the same shape and dtype as the input.

    Notes
    -----
    - Uses Gaussian blur with sigmaX=2 to create the unsharp mask.
    - The operation is performed using `cv2.addWeighted`.
    - Does not modify the input image in-place.
    """
    # Apply Gaussian blur to create the mask
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=2)

    # Combine original image with the negative blurred image
    unsharp = cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
    return unsharp
