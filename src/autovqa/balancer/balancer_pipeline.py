"""Balancing pipeline module for advanced data balancing operations."""

from typing import List, Optional

import pandas as pd
from loguru import logger

from .balancer import Balancer
from .config import (
    FEATURE_COLUMNS,
    KEEP_OUTLIERS,
    LIMIT_PERCENT,
    NUMERIC_COLUMNS,
    PERCENT_MIN_SAMPLES,
    REASON_DEPTH_WEIGHT,
    TOP_PERCENT,
)


def balancer_pipeline(
    df_raw: pd.DataFrame,
    numeric_columns: List[str] = NUMERIC_COLUMNS,
    feature_columns: List[str] = FEATURE_COLUMNS,
    reason_depth_weight: int = REASON_DEPTH_WEIGHT,
    percent_min_samples: float = PERCENT_MIN_SAMPLES,
    top_percent: float = TOP_PERCENT,
    limit_percent: float = LIMIT_PERCENT,
    keep_outliers: bool = KEEP_OUTLIERS,
    output_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Balance labels across multiple features with weighted scoring.

    Steps: compute overall_score → sort by score → balance each feature
    → return balanced DataFrame.

    Args:
        df_raw: Input DataFrame.
        numeric_columns: Columns for overall_score computation.
            Default from config.toml.
        feature_columns: Columns to balance sequentially.
            Default from config.toml.
        reason_depth_weight: Weight for 'vqac_reason_depth_response'.
            Default from config.toml (4).
        percent_min_samples: Min percent to keep labels.
            Default from config.toml (0.01).
        top_percent: Keep top X% labels by frequency.
            Default from config.toml (0.9).
        limit_percent: Max percent difference between classes.
            Default from config.toml (10).
        keep_outliers: Keep rare labels removed in filtering.
            Default from config.toml (True).
        output_path: CSV save path. Default is None.

    Returns:
        Balanced DataFrame.

    Raises:
        ValueError: If required columns not found.
    """
    logger.info("Starting advanced balancer pipeline")
    logger.info(
        f"Parameters: reason_depth_weight={reason_depth_weight}, "
        f"percent_min_samples={percent_min_samples}, "
        f"top_percent={top_percent}, limit_percent={limit_percent}, "
        f"keep_outliers={keep_outliers}"
    )
    logger.info(f"Numeric columns: {numeric_columns}")
    logger.info(f"Feature columns to balance: {feature_columns}")

    # Get initial statistics
    initial_rows = len(df_raw)
    logger.info(f"Initial data: {initial_rows} rows")

    for col in feature_columns:
        if col in df_raw.columns:
            unique_labels = df_raw[col].nunique()
            logger.info(f"  - Column '{col}': {unique_labels} unique labels")

    # Apply advanced balancing pipeline
    df_balanced = Balancer.apply_balancing_pipeline(
        df_raw=df_raw,
        numeric_columns=numeric_columns,
        feature_columns=feature_columns,
        reason_depth_weight=reason_depth_weight,
        percent_min_samples=percent_min_samples,
        top_percent=top_percent,
        limit_percent=limit_percent,
        keep_outliers=keep_outliers,
        output_path=output_path,
    )

    # Get final statistics
    final_rows = len(df_balanced)
    logger.info(f"Final data: {final_rows} rows")

    for col in feature_columns:
        if col in df_balanced.columns:
            unique_labels = df_balanced[col].nunique()
            logger.info(f"  - Column '{col}': {unique_labels} unique labels")

    # Calculate reduction statistics
    rows_removed = initial_rows - final_rows
    if initial_rows > 0:
        reduction_percent = 100 * rows_removed / initial_rows
    else:
        reduction_percent = 0
    logger.info(f"Reduced: {rows_removed} rows ({reduction_percent:.2f}%)")

    logger.info("Advanced balancer pipeline completed successfully")
    return df_balanced
