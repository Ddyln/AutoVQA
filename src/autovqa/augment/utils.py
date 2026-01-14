import random
from typing import Optional

from loguru import logger


def get_target_levels(
    samples_remain: list[int], probabilities: list[float]
) -> Optional[list[int]]:
    """
    Select two different target levels based on remaining samples and probabilities.

    Args:
        samples_remain: List of remaining samples for each level (1-indexed).
        probabilities: List of probabilities for each level (must sum to 1.0).

    Returns:
        List of two different levels (1-5), or None if insufficient samples.
        If only one level available, returns that level twice.
    """

    if sum(samples_remain) == 0:
        logger.debug("All target levels have been met.")
        return None

    available_levels = [i + 1 for i, remain in enumerate(samples_remain) if remain > 0]

    if not available_levels:
        logger.debug("No available levels with remaining samples.")
        return None

    if len(available_levels) == 1:
        level = available_levels[0]
        logger.debug(f"Only one level available: {level}, returning it twice")
        return [level, level]

    available_probs = [
        probabilities[i] for i in range(len(probabilities)) if samples_remain[i] > 0
    ]

    total_prob = sum(available_probs)
    if total_prob > 0:
        normalized_probs = [p / total_prob for p in available_probs]
    else:
        normalized_probs = [1.0 / len(available_levels)] * len(available_levels)

    first_level = random.choices(available_levels, weights=normalized_probs, k=1)[0]

    remaining_levels = [lvl for lvl in available_levels if lvl != first_level]
    remaining_probs = [
        normalized_probs[i]
        for i, lvl in enumerate(available_levels)
        if lvl != first_level
    ]

    total_remaining_prob = sum(remaining_probs)
    if total_remaining_prob > 0:
        remaining_probs = [p / total_remaining_prob for p in remaining_probs]
    else:
        remaining_probs = [1.0 / len(remaining_levels)] * len(remaining_levels)

    second_level = random.choices(remaining_levels, weights=remaining_probs, k=1)[0]

    selected_levels = [first_level, second_level]

    logger.debug(
        f"Selected levels: {selected_levels} from available: {available_levels}"
    )

    return selected_levels
