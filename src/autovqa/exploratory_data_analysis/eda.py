import os
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

from .key_mapper import KeyMapper
from .processors import MainObjectProcessor, SceneTypeProcessor
from .utils import Utils


class EDA:
    """Exploratory Data Analysis pipeline for VQA data processing."""

    def __init__(self, data: list, history: Optional[list] = None):
        """Initialize the EDA pipeline with JSON data.

        Args:
            data (list): The JSON data to analyze.
            history (list, optional): A list to keep track of operations
                performed. Defaults to None.
        """
        self.utils = Utils()
        self.scene_type_processor = SceneTypeProcessor()
        self.df = self.utils.to_df(KeyMapper.transform_keys(data))
        self.history = history if history is not None else []

    def _drop_duplicates(self):
        """Drop duplicate rows in the DataFrame.

        Handles columns with lists by converting to string for duplicate
        detection.
        """
        try:
            self.df.drop_duplicates(inplace=True)
        except TypeError:
            df_temp = self.df.copy()

            for col in df_temp.columns:
                if df_temp[col].dtype == "object" and len(df_temp) > 0:
                    sample_val = df_temp.loc[0, col]
                    if isinstance(sample_val, (list, dict)):
                        df_temp[col] = df_temp[col].astype(str)

            df_temp.drop_duplicates(inplace=True)
            self.df = self.df.loc[df_temp.index]

    def _filter_invalid_rows(self):
        """Convert columns to types and filter invalid rows.

        Filters out rows where list columns have inconsistent
        lengths or invalid data.
        """

        def is_invalid_row(row):
            """Check if a row contains invalid list data."""
            try:
                row_lists = row.tolist()

                if not all(isinstance(x, list) for x in row_lists):
                    return True

                if any(len(x) == 0 for x in row_lists):
                    return True

                lengths = [len(x) for x in row_lists]
                return len(set(lengths)) != 1

            except Exception:
                return True

        # Convert columns to appropriate types
        for col in self.utils.get_numeric_columns():
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        for col in self.utils.get_str_columns():
            self.df[col] = self.df[col].astype(str)

        # Filter rows with invalid list data (check first 5 list columns)
        list_columns = self.utils.get_list_cols()[:5]
        if list_columns:
            mask = self.df[list_columns].apply(is_invalid_row, axis=1)
            self.df = self.df[~mask]

    def _clean_data(self):
        """Clean DataFrame: remove NaN, duplicates, invalid rows."""
        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        self._drop_duplicates()
        self._filter_invalid_rows()

        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    def _process_columns(self) -> None:
        """Process columns to extract scene types and main objects info."""
        self.df = self.scene_type_processor.process(self.df)
        self.df = MainObjectProcessor.process(self.df)

    def _get_overview_statistics(self) -> dict:
        """Get overview statistics of the DataFrame.

        Returns:
            dict: Overview statistics including shape, missing values,
                and column types.
        """
        if self.df.empty:
            logger.info("DataFrame is empty.")
            return {}

        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]

        missing_values_sorted = sorted(
            [(column, int(count)) for column, count in missing_data.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        categorical_columns = self.df.select_dtypes(include=["object"]).columns
        numeric_columns = self.df.select_dtypes(include=["number"]).columns
        if len(missing_data) > 0:
            total_missing_cells = int(missing_data.sum())
        else:
            total_missing_cells = 0
        return {
            "missing_values": missing_values_sorted,
            "missing_values_count": len(missing_values_sorted),
            "total_missing_cells": (total_missing_cells),
            "number_of_rows": int(self.df.shape[0]),
            "number_of_columns": int(self.df.shape[1]),
            "categorical_columns": len(categorical_columns),
            "numeric_columns": len(numeric_columns),
        }

    def _write_scene_report(self, output_dir: str) -> str:
        """Write scene types report to a separate Excel file.

        Args:
            output_dir (str): Directory to save the report.

        Returns:
            str: Path to the created file.
        """
        scene_types_file = os.path.join(output_dir, "scene_types_report.xlsx")
        SceneTypeProcessor.generate_report(self.df).to_excel(
            scene_types_file, sheet_name="Scene_Types", index=True
        )
        return scene_types_file

    def _write_objects_report(self, output_dir: str) -> str:
        """Write main objects report to a separate Excel file.

        Args:
            output_dir (str): Directory to save the report.

        Returns:
            str: Path to the created file.
        """
        main_objs_path = os.path.join(output_dir, "main_objects_report.xlsx")
        MainObjectProcessor.generate_report(self.df).to_excel(
            main_objs_path, sheet_name="Main_Objects", index=True
        )
        return main_objs_path

    def _write_stats_report(
        self,
        output_dir: str,
        stats: dict,
        expl_stats_df: pd.DataFrame,
        numeric_columns,
        str_columns,
        label_columns,
    ) -> str:
        """Write main statistics report to Excel file.

        Args:
            output_dir (str): Directory to save the report.
            stats (dict): Overview statistics.
            expl_stats_df (pd.DataFrame): Detailed statistics DataFrame.
            numeric_columns: Numeric column names.
            str_columns: String column names.
            label_columns: Label column names.

        Returns:
            str: Path to the created file.
        """
        file_name = os.path.join(output_dir, "eda_main_statistics.xlsx")
        with pd.ExcelWriter(file_name) as w:
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(w, sheet_name="Overview", index=True)

            available_numeric = [col for col in numeric_columns]
            available_str = [col for col in str_columns]
            available_labels = [col for col in label_columns]

            if available_numeric:
                expl_stats_df[available_numeric].to_excel(
                    w, sheet_name="Numeric", index=True
                )
            if available_str:
                expl_stats_df[available_str].to_excel(
                    w, sheet_name="String", index=True
                )
            if available_labels:
                expl_stats_df[available_labels].to_excel(
                    w, sheet_name="Labels", index=True
                )

        return file_name

    def get_report_on_data(self, output_dir: str = "report") -> None:
        """Generate statistics reports and save to the specified directory.

        Args:
            output_dir (str): Directory path to save the reports.
                Defaults to 'report'. Three Excel files will be created:
                - eda_main_statistics.xlsx
                - scene_types_report.xlsx
                - main_objects_report.xlsx
        """
        if self.df.empty:
            logger.info("DataFrame is empty.")
            return

        os.makedirs(output_dir, exist_ok=True)

        try:
            stats = self._get_overview_statistics()
        except Exception as e:
            logger.info(f"Error getting overview statistics: {e}")
            stats = {}

        logger.info("Generating detailed statistics report...")
        numeric_columns = self.df.select_dtypes(include="number").columns

        list_column_names = self.utils.get_list_cols()
        list_columns = [col for col in list_column_names]

        str_columns = [
            col
            for col in self.df.select_dtypes(include="object").columns
            if col not in list_columns
        ]

        label_columns = [col for col in self.df.columns if "Label" in col]

        stats_columns = numeric_columns.tolist() + str_columns
        expl_stats_df = pd.DataFrame(
            self.df[stats_columns].describe(include="all").to_dict()
        )

        logger.info("Writing reports...")
        results = {}

        try:
            results["Main statistics"] = self._write_stats_report(
                output_dir,
                stats,
                expl_stats_df,
                numeric_columns,
                str_columns,
                label_columns,
            )
            logger.info("  ✓ Main statistics report")
        except Exception as exc:
            logger.info(f"  ✗ Main statistics: {exc}")

        try:
            results["Scene types"] = self._write_scene_report(output_dir)
            logger.info("  ✓ Scene types report")
        except Exception as exc:
            logger.info(f"  ✗ Scene types: {exc}")

        try:
            results["Main objects"] = self._write_objects_report(output_dir)
            logger.info("  ✓ Main objects report")
        except Exception as exc:
            logger.info(f"  ✗ Main objects: {exc}")

        if results:
            logger.info("Reports saved to:")
            for name, path in results.items():
                logger.info(f"  - {name}: {path}")

    def _calc_score_agg(self, aggregation_type: str = "median") -> None:
        """Calculate score aggregations based on the specified type.

        Args:
            aggregation_type (str): Type of aggregation
                ('median', 'mean', 'max', 'min').
        """
        score_columns = []
        for col in self.df.columns:
            if "Score_for_answers" in col:
                score_columns.append(col)
        if not score_columns:
            raise ValueError("No columns found with 'Score_for_answers'")

        aggregation_funcs = {
            "median": np.median,
            "mean": np.mean,
            "max": np.max,
            "min": np.min,
        }

        func = aggregation_funcs.get(aggregation_type, np.median)

        for col in score_columns:
            new_col_name = col.replace(
                "Score_for_answers",
                f"Score_answers_{aggregation_type}",
            )
            self.df[new_col_name] = self.df[col].apply(
                func
            )  # type: ignore[call-overload]

    def _create_label_columns(self, thres_type: str) -> None:
        """Create label columns based on threshold values.

        Args:
            thres_type (str): Type of threshold
                ('median', 'mean', 'max', 'min').
        """
        numeric_columns = self.df.select_dtypes(include=["number"]).columns

        threshold_funcs = {
            "median": lambda col: self.df[col].median(),
            "mean": lambda col: self.df[col].mean(),
            "max": lambda col: self.df[col].max(),
            "min": lambda col: self.df[col].min(),
        }
        func_call = threshold_funcs.get(thres_type, threshold_funcs["median"])

        for col in numeric_columns:
            threshold_value = func_call(col)
            label_col_name = f"{col}_Label"
            self.df[label_col_name] = self.df[col].apply(
                lambda x: "Passed" if x >= threshold_value else "Failed"
            )

    def run(
        self,
        aggregation_type: str = "median",
        generate_report: bool = True,
        output_dir: str = "report",
    ) -> None:
        """Run the complete EDA pipeline.

        Args:
            aggregation_type (str): Aggregation type for scoring and
                labeling ('median', 'mean', 'max', 'min').
                Defaults to 'median'.
            generate_report (bool): Whether to generate statistics report.
                Defaults to True.
            output_dir (str): Directory path to save reports.
                Defaults to 'report'.
        """
        logger.info("Running EDA pipeline...")

        try:
            self._clean_data()
            self._process_columns()
            self._calc_score_agg(aggregation_type)
            self._create_label_columns(thres_type=aggregation_type)
            if generate_report:
                self.get_report_on_data(output_dir=output_dir)

        except Exception as e:
            logger.error(f"Error during EDA processing: {e}")
            return

        logger.info("EDA pipeline completed.")

    def get_dataframe(self) -> pd.DataFrame:
        """Get the processed DataFrame.

        Returns:
            pd.DataFrame: The processed DataFrame.
        """
        return self.df
