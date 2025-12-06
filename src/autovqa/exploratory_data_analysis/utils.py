from typing import Optional

import pandas as pd

from .config import (
    EIP_FIELD_CONFIG,
    ETP_FIELD_CONFIG,
    IDP_FIELD_CONFIG,
    LIST_FIELD_CONFIG,
    NUMERIC_FIELD_CONFIG,
    STR_FIELD_CONFIG,
    VQAC_FIELD_CONFIG,
)


class Utils:
    """Utility class for extracting and managing structured VQA data fields."""

    def __init__(self):
        """Initialize utils with field configuration patterns."""
        self.field_patterns = [
            ETP_FIELD_CONFIG,
            EIP_FIELD_CONFIG,
            IDP_FIELD_CONFIG,
            VQAC_FIELD_CONFIG,
        ]

    def to_df(self, data: list, cols: Optional[list] = None) -> pd.DataFrame:
        """Convert JSON data to DataFrame with specified columns.

        Args:
            data (list): The JSON data to convert.
            cols (list, optional): Base columns to include in
                addition to field configs. Defaults to ['index',
                'question', 'answers', 'image_url', 'image_name'].

        Returns:
            pd.DataFrame: DataFrame with normalized JSON data and
                selected columns.
        """
        if cols is None:
            cols = [
                "index",
                "question",
                "answers",
                "image_url",
                "image_name",
            ]

        df = pd.json_normalize(data, sep="_")
        all_columns = (
            ETP_FIELD_CONFIG
            + EIP_FIELD_CONFIG
            + IDP_FIELD_CONFIG
            + VQAC_FIELD_CONFIG
            + cols
        )
        return df[all_columns].copy()

    @staticmethod
    def get_field_columns(field_type: Optional[str] = None) -> list:
        """Get column names for a specific field type.

        Args:
            field_type (str, optional): The field type to retrieve.
                Options: 'ETP', 'EIP', 'IDP', 'VQAC'.
                If None, returns all field columns.

        Returns:
            list: List of column names for the specified field type.
        """
        if field_type == "ETP":
            return ETP_FIELD_CONFIG
        elif field_type == "EIP":
            return EIP_FIELD_CONFIG
        elif field_type == "IDP":
            return IDP_FIELD_CONFIG
        elif field_type == "VQAC":
            return VQAC_FIELD_CONFIG

        # Return all field columns if no type specified
        FIELD_LIST = []
        FIELD_LIST.extend(ETP_FIELD_CONFIG)
        FIELD_LIST.extend(EIP_FIELD_CONFIG)
        FIELD_LIST.extend(IDP_FIELD_CONFIG)
        FIELD_LIST.extend(VQAC_FIELD_CONFIG)

        return FIELD_LIST

    def get_numeric_columns(self) -> list:
        """Get list of numeric column names.

        Returns:
            list: Column names that contain numeric data.
        """
        return NUMERIC_FIELD_CONFIG

    def get_str_columns(self) -> list:
        """Get list of string column names.

        Returns:
            list: Column names that contain string data.
        """
        return STR_FIELD_CONFIG

    def get_list_cols(self) -> list:
        """Get list of list-type column names.

        Returns:
            list: Column names that contain list data.
        """
        return LIST_FIELD_CONFIG
