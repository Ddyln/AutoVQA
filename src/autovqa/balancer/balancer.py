from typing import List, Optional

import pandas as pd
from loguru import logger


class Balancer:
    def __init__(self):
        pass

    @staticmethod
    def balance_labels(
        df: pd.DataFrame,
        col: str,
        percent_min_samples: float = 0.01,
        top_percent: float = 0.9,
        limit_percent: float = 10,
        keep_outliers: bool = False,
    ) -> pd.DataFrame:
        """
        Balance imbalanced data by:
        1. Removing rare labels (below min sample percent) and keeping
           only top X% labels.
        2. Undersampling remaining labels so the max difference between
           classes does not exceed `limit_percent`.

        Args:
            df (pd.DataFrame): Input DataFrame.
            col (str): Name of label column.
            percent_min_samples (float): Minimum percent of samples for a
                label to be kept.
            top_percent (float): Keep labels covering top X% of data
                (by cumulative frequency).
            limit_percent (float): Max allowed percent difference between
                smallest and other classes after undersampling.
            keep_outliers (bool): If True, keep rare labels removed in
                step 1.

        Returns:
            pd.DataFrame: Balanced DataFrame (copy).
        """

        if not isinstance(df, pd.DataFrame):
            logger.error("Input df must be a pandas DataFrame.")
            raise

        try:
            counts = df[col].value_counts()
            total = counts.sum()
            if total == 0:
                logger.warning("Input DataFrame is empty.")
                return df.copy()
        except Exception as e:
            logger.info(f"Column '{col}' not found. Error: {e}")
            raise e

        # 1. Remove rare classes
        min_samples = int(max(total * percent_min_samples, 1))
        outliers: list = []
        if keep_outliers:
            outlier_mask = counts < min_samples
            outliers = counts[outlier_mask].index.tolist()
        keep_mask = counts >= min_samples
        counts = counts[keep_mask]

        # 2. Keep labels by top_percent
        sorted_counts = counts.sort_values(ascending=False)
        cumulative_ratio = sorted_counts.cumsum() / total
        labels_to_keep = cumulative_ratio[
            cumulative_ratio <= top_percent
        ].index.tolist()
        if len(labels_to_keep) == 0:
            logger.warning("No labels to keep after filtering by top_percent.")
            return df.copy()

        # 3. Find min sample count
        min_count = counts[labels_to_keep].min()

        # 4. Undersampling
        indices_to_keep = []
        for label in counts.index:
            if label in labels_to_keep:
                if limit_percent != 100:
                    # Limit max allowed samples for each class
                    numerator = 1 + limit_percent / 100
                    denominator = 1 - limit_percent / 100
                    max_allowed = int(min_count * (numerator / denominator))
                else:
                    max_allowed = -1  # keep all
                label_indices = df[df[col] == label].index[:max_allowed]
            else:
                label_indices = df[df[col] == label].index
            indices_to_keep.extend(label_indices)

        # 5. Keep outliers if needed
        if keep_outliers and outliers:
            indices_to_keep.extend(df[df[col].isin(outliers)].index)

        num_original = df[col].nunique()
        num_balanced = len(set(df.loc[indices_to_keep, col]))
        logger.info(f"Balanced labels: {num_original} -> {num_balanced}")
        return df.loc[indices_to_keep].copy()

    @staticmethod
    def apply_balancing_pipeline(
        df_raw: pd.DataFrame,
        numeric_columns: List[str],
        feature_columns: List[str],
        reason_depth_weight: int = 4,
        percent_min_samples: float = 0.01,
        top_percent: float = 0.9,
        limit_percent: float = 10,
        keep_outliers: bool = True,
        output_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Pipeline:
        - Compute overall_score (weighted for
          'vqac_reason_depth_response').
        - Sort by overall_score to prioritize high-quality samples.
        - Balance sequentially by each feature in feature_columns.
        - Return balanced DataFrame (and save to file if output_path is
          given).
        """
        # Input validation
        for col in numeric_columns:
            if col not in df_raw.columns:
                msg = f"Numeric column '{col}' not found in DataFrame."
                logger.error(msg)
                raise ValueError(msg)
        for col in feature_columns:
            if col not in df_raw.columns:
                msg = f"Feature column '{col}' not found in DataFrame."
                logger.error(msg)
                raise ValueError(msg)
        if "vqac_reason_depth_response" not in numeric_columns:
            msg = (
                "'vqac_reason_depth_response' not in numeric_columns. "
                "Weighting may not apply."
            )
            logger.warning(msg)

        temp_df = df_raw[numeric_columns].copy()
        if "vqac_reason_depth_response" in temp_df.columns:
            temp_df["vqac_reason_depth_response"] *= reason_depth_weight
            total_weight = temp_df.shape[1] + reason_depth_weight - 1
        else:
            total_weight = temp_df.shape[1]

        df = df_raw[feature_columns].copy()
        df["overall_score"] = temp_df.sum(axis=1) / total_weight
        df["id"] = df.index

        # Sort by overall_score
        df_balanced = df.sort_values(by="overall_score", ascending=False)
        df_balanced.reset_index(drop=True, inplace=True)

        # Apply balancing for each feature
        for col in feature_columns:
            df_balanced = Balancer.balance_labels(
                df_balanced,
                col,
                percent_min_samples=percent_min_samples,
                top_percent=top_percent,
                limit_percent=limit_percent,
                keep_outliers=keep_outliers,
            )
            df_balanced = df_balanced.reset_index(drop=True)

        # Map back to original df_raw
        selected_index = df_balanced["id"].tolist()
        df_filter = df_raw.iloc[selected_index].reset_index(drop=True)

        if output_path:
            df_filter.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Balanced data saved to {output_path}")

        return df_filter.copy()
