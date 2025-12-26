import os
from collections import Counter
from typing import Optional, Tuple

import cv2

# import numpy as np


def find_most_common_image_size(
    folder_path: str, extension: str = ".jpg"
) -> Optional[Tuple[int, int]]:
    """
    Find the most common image size (height, width) in a folder
    for a given file extension.

    Parameters
    ----------
    folder_path : str
        Path to the folder containing images.
    extension : str, optional
        File extension to filter images,
        e.g., ".jpg", ".png". Default is ".jpg".

    Returns
    -------
    Optional[Tuple[int, int]]
        The most common image size as (height, width),
        or None if no valid images found.

    Notes
    -----
    - Uses OpenCV to read images (BGR format).
    - Ignores images that cannot be read.
    - Prints progress every 1000 images.
    """
    # size_counter = Counter()
    size_counter: Counter[Tuple[int, int]] = Counter()

    # List all files with the given extension
    image_files = [f for f in os.listdir(folder_path) if f.endswith(extension)]

    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        img = cv2.imread(image_path)
        # img: Optional[np.ndarray] = cv2.imread(image_path)

        if img is not None:
            h, w = img.shape[:2]
            size_counter[(w, h)] += 1
        else:
            print(f"[ERROR] Could not read {image_file}")

        if (idx + 1) % 1000 == 0 or (idx + 1) == len(image_files):
            print(f"Scanned {idx + 1}/{len(image_files)} images")

    most_common = size_counter.most_common(1)
    if most_common:
        (w, h), count = most_common[0]
        print(f"\nMost common size: ({h}x{w}) - {count} images")
        return (h, w)
    else:
        print("No valid images found.")
        return None
