import re
from typing import List

import pandas as pd


class ReportGenerator:
    """Utility class for generating frequency reports from DataFrame
    columns.
    """

    @staticmethod
    def gen_freq_report(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """Generate a frequency report for a specific column.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to analyze.

        Returns:
            pd.DataFrame: A DataFrame with frequency counts for the
                column values.

        Raises:
            ValueError: If the specified column is not found in
                DataFrame.
        """
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame.")

        report_df = df[column_name].value_counts().reset_index()
        report_df.columns = [column_name, "Frequency"]
        return report_df


class SceneTypeProcessor:
    """Processor for analyzing and normalizing scene type data in IDP
    fields.
    """

    def __init__(self):
        """Initialize the scene type processor."""
        self._frequency_dict = None

    def _build_freq_dict(self, df: pd.DataFrame, column_name: str) -> dict:
        """Build a frequency dictionary for the specified column.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to analyze.

        Returns:
            dict: A dictionary with items as keys and their frequencies
                as values.
        """
        frequency_dict = df[column_name].explode().value_counts().to_dict()
        return frequency_dict

    def _get_most_frequent_item(self, scene_type_list: List[str]) -> str:
        """Get the item with the highest frequency from a list.

        Args:
            scene_type_list (List[str]): A list of scene types to check.

        Returns:
            str: The scene type with the highest frequency.

        Raises:
            ValueError: If frequency dictionary is not initialized.
        """
        if self._frequency_dict is None:
            raise ValueError(
                "Frequency dictionary is not initialized. Run process() first."
            )

        return max(scene_type_list, key=lambda x: self._frequency_dict[x])

    def process(
        self, df: pd.DataFrame, column_name: str = "idp_Img_scene_type"
    ) -> pd.DataFrame:
        """Process and normalize scene type column in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to process.
                Defaults to 'idp_Img_scene_type'.

        Returns:
            pd.DataFrame: A DataFrame with processed and normalized
                scene type data.
        """
        df_processed = df.copy()

        # Split scene types into individual words and normalize
        df_processed[column_name] = df_processed[column_name].apply(
            lambda x: [
                word.strip()
                for word in re.split(r"[ /:;@!,_\\]+", x.lower())
                if word.strip()
            ]
        )

        # Build frequency dictionary for all scene types
        self._frequency_dict = self._build_freq_dict(df_processed, column_name)

        # Select most frequent scene type from each list
        df_processed[column_name] = df_processed[column_name].apply(
            self._get_most_frequent_item
        )

        return df_processed

    def get_frequency_dict(self) -> dict:
        """Get the frequency dictionary of scene types.

        Returns:
            dict: A dictionary with scene types and their frequencies.
                Returns None if not yet initialized.
        """
        if self._frequency_dict is None:
            print(
                "Warning: Frequency dictionary is not initialized. "
                "Run process() first."
            )
        return self._frequency_dict

    @staticmethod
    def generate_report(
        df: pd.DataFrame, column_name: str = "idp_Img_scene_type"
    ) -> pd.DataFrame:
        """Generate a frequency report for scene types.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to analyze.
                Defaults to 'idp_Img_scene_type'.

        Returns:
            pd.DataFrame: A DataFrame with scene type frequency report.
        """
        return ReportGenerator.gen_freq_report(df, column_name)


class MainObjectProcessor:
    """Processor for normalizing main object data in IDP fields."""

    @staticmethod
    def process(
        df: pd.DataFrame, column_name: str = "idp_Img_main_object"
    ) -> pd.DataFrame:
        """Process and normalize main object column in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to process.
                Defaults to 'idp_Img_main_object'.

        Returns:
            pd.DataFrame: A DataFrame with normalized main object data.
        """
        df_processed = df.copy()

        # Convert to lowercase for normalization
        df_processed[column_name] = df_processed[column_name].apply(
            lambda x: x.lower() if isinstance(x, str) else None
        )

        return df_processed

    @staticmethod
    def generate_report(
        df: pd.DataFrame, column_name: str = "idp_Img_main_object"
    ) -> pd.DataFrame:
        """Generate a frequency report for main objects.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column_name (str): The column name to analyze.
                Defaults to 'idp_Img_main_object'.

        Returns:
            pd.DataFrame: A DataFrame with main object frequency report.
        """
        return ReportGenerator.gen_freq_report(df, column_name)
