"""Pipeline function for Exploratory Data Analysis (EDA)."""

from typing import Optional

import pandas as pd

from .eda import EDA


def eda_pipeline(
    data: list,
    output_dir: str = "report",
    generate_report: bool = True,
    aggregation_type: str = "median",
    history: Optional[list] = None,
) -> pd.DataFrame:
    """Execute EDA pipeline and return processed DataFrame.

    This function performs exploratory data analysis on VQA data including
    data cleaning, feature processing, score aggregation, and optional
    report generation.

    Args:
        data (list): The JSON data to analyze.
        output_dir (str, optional): Directory path to save reports.
            Defaults to "report".
        generate_report (bool, optional): Whether to generate statistics
            reports. Defaults to True.
        aggregation_type (str, optional): Aggregation type for scoring and
            labeling ('median', 'mean', 'max', 'min'). Defaults to "median".
        history (list, optional): A list to keep track of operations performed.
            Defaults to None.

    Returns:
        pd.DataFrame: The processed DataFrame after EDA operations.

    Example:
        >>> import json
        >>> with open('data.json', 'r') as f:
        ...     data = json.load(f)
        >>> df = eda_pipeline(
        ...     data,
        ...     output_dir="output",
        ...     generate_report=True
        ... )
    """
    eda = EDA(data=data, history=history)
    eda.run(
        aggregation_type=aggregation_type,
        generate_report=generate_report,
        output_dir=output_dir,
    )
    return eda.get_dataframe()
