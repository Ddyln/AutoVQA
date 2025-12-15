"""Filter pipeline module.

This module provides the main filter_pipeline function for filtering data.
"""

from .filter import Filter


def filter_pipeline(
    data, column_names=None, threshold=0.5, keep_columns=None, show_stats=True
):
    """Run the filter pipeline to process and filter data.

    This function uses the Filter.filter() static method to filter data
    based on label thresholds. It adds a 'record_to_keep' column,
    optionally shows statistics, filters the data, and returns the
    cleaned result with reset index.

    Args:
        data: DataFrame to be filtered.
        column_names (list, optional): List of column names to check for
            filtering. If None, all columns will be used.
        threshold (float, optional): Minimum ratio of "Passed" labels
            required (0.0-1.0). Defaults to 0.5.
        keep_columns (list, optional): List of columns to keep in the
            final result. If None, all columns except 'record_to_keep'
            are kept.
        show_stats (bool, optional): Whether to log statistics about
            filtered records. Defaults to True.

    Returns:
        Filtered DataFrame after applying the threshold filter with
            reset index.

    Example:
        >>> filtered_df = filter_pipeline(
        ...     df, column_names=['col1', 'col2'], threshold=0.6
        ... )
        >>> filtered_df = filter_pipeline(
        ...     df, column_names=['col1', 'col2'],
        ...     keep_columns=['col1', 'col2', 'col3']
        ... )
        >>> filtered_df = filter_pipeline(df)  # Uses default threshold
    """
    if column_names is None:
        # If no columns specified, use all columns from data
        column_names = [column for column in data.columns if "Label" in column]

    # Apply the filter using the static method
    filtered_data = Filter.filter(
        data, column_names, threshold, keep_columns, show_stats
    )

    return filtered_data
