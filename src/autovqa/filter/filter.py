"""Filter pipeline module.

This module defines the complete filtering pipeline for data processing.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Filter:
    """A pipeline for applying multiple filters to data."""

    def __init__(self):
        """Initialize the filtering pipeline components."""
        self.filters = []
        self.filtered_data = None

    @staticmethod
    def filter(
        data,
        column_names: list,
        threshold: float = 0.5,
        keep_columns=None,
        show_stats=True,
    ):
        """Filter DataFrame based on threshold for labeled columns.

        Args:
            data: DataFrame to be filtered.
            column_names: List of column names to check.
            threshold: Minimum ratio of "Passed" labels required (0.0-1.0).
            keep_columns (list, optional): List of columns to keep in the
                final result. If None, all columns except 'record_to_keep'
                are kept.
            show_stats (bool, optional): Whether to log statistics about
                filtered records. Defaults to True.

        Returns:
            DataFrame: Filtered data containing only rows that meet
                the threshold, with reset index.
        """

        def check_row(row):
            passed_count = row[column_names].tolist().count("Passed")
            required_count = threshold * len(column_names)
            return passed_count >= required_count

        # Add record_to_keep column using vectorized operations
        passed_counts = (data[column_names] == "Passed").sum(axis=1)
        required_count = threshold * len(column_names)
        data["record_to_keep"] = passed_counts >= required_count

        # Show statistics if requested
        if show_stats:
            keep_count = data["record_to_keep"].sum()
            total_count = len(data)
            if total_count > 0:
                keep_percentage = (keep_count / total_count) * 100
            else:
                keep_percentage = 0

            logger.info(
                f"Records to keep: {keep_count} / {total_count} "
                f"({keep_percentage:.2f}%)"
            )

        # Filter data
        filtered_data = data[data["record_to_keep"]].copy()

        # Drop the temporary column if not explicitly requested
        if keep_columns is not None:
            filtered_data = filtered_data[keep_columns]
        else:
            filtered_data = filtered_data.drop(columns=["record_to_keep"])

        # Reset index
        filtered_data.reset_index(drop=True, inplace=True)

        logger.info(
            f"Filtered {len(data)} rows to {len(filtered_data)} rows "
            f"(threshold: {threshold})"
        )
        return filtered_data

    def run(self, data):
        """Run the filtering process on the provided data.

        Args:
            data: Input data to be filtered.

        Returns:
            Filtered data after applying all filters.
        """
        logger.info("Starting filter pipeline")
        self.filtered_data = data

        for filter_func in self.filters:
            self.filtered_data = filter_func(self.filtered_data)

        logger.info("Filter pipeline completed")
        return self.filtered_data

    def add_filter(self, filter_func):
        """Add a new filter to the pipeline.

        Args:
            filter_func: A callable filter function to add.
        """
        self.filters.append(filter_func)
        logger.info(f"Added filter: {filter_func.__name__}")

    def remove_filter(self, filter_func):
        """Remove a filter from the pipeline.

        Args:
            filter_func: The filter function to remove.
        """
        if filter_func in self.filters:
            self.filters.remove(filter_func)
            logger.info(f"Removed filter: {filter_func.__name__}")

    def clear_filters(self):
        """Clear all filters from the pipeline."""
        self.filters.clear()
        logger.info("Cleared all filters")

    def get_filtered_data(self):
        """Return the filtered data.

        Returns:
            The most recently filtered data, or None if no filtering
                has occurred.
        """
        return self.filtered_data
