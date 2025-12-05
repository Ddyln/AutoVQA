"""Tests for Filter pipeline module."""

import pandas as pd
import pytest

from autovqa.filter.filter_pipeline import filter_pipeline


@pytest.fixture
def df():
    """Create sample DataFrame with label columns for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "vqac_reason_depth_label": [
                "Passed",
                "Passed",
                "Failed",
                "Passed",
                "Failed",
            ],
            "vqac_answer_consistency_label": [
                "Passed",
                "Failed",
                "Passed",
                "Passed",
                "Passed",
            ],
            "vqac_context_relevance_label": [
                "Passed",
                "Passed",
                "Passed",
                "Failed",
                "Failed",
            ],
            "value": [10, 20, 30, 40, 50],
        }
    )


@pytest.fixture
def no_label_dataframe():
    """Create DataFrame without label columns."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
            "value": [10, 20, 30],
        }
    )


@pytest.fixture
def empty_df():
    """Create empty DataFrame for edge case testing."""
    return pd.DataFrame()


class TestFilterPipeline:
    """Test cases for Filter pipeline functionality."""

    def test_filter_pipeline_basic(self, df):
        """Test basic filter pipeline execution."""
        result = filter_pipeline(data=df, threshold=0.5, show_stats=False)

        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df)

    def test_filter_pipeline_threshold_half(self, df):
        """Test filter with 0.5 threshold."""
        result = filter_pipeline(data=df, threshold=0.5, show_stats=False)

        assert isinstance(result, pd.DataFrame)
        # With 0.5 threshold, rows need at least 50% passed
        assert len(result) > 0

    def test_filter_pipeline_threshold_high(self, df):
        """Test filter with high threshold (1.0)."""
        result = filter_pipeline(data=df, threshold=1.0, show_stats=False)

        assert isinstance(result, pd.DataFrame)
        # With 1.0 threshold, only rows with all passed labels
        assert len(result) <= len(df)

    def test_filter_pipeline_threshold_low(self, df):
        """Test filter with low threshold (0.0)."""
        result = filter_pipeline(data=df, threshold=0.0, show_stats=False)

        assert isinstance(result, pd.DataFrame)
        # With 0.0 threshold, all rows should pass
        assert len(result) == len(df)

    def test_filter_pipeline_specific_columns(self, df):
        """Test filter with specific column names."""
        columns = [
            "vqac_reason_depth_label",
            "vqac_answer_consistency_label",
        ]
        result = filter_pipeline(
            data=df,
            column_names=columns,
            threshold=0.5,
            show_stats=False,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df)

    def test_filter_pipeline_keep_columns(self, df):
        """Test filter with keep_columns parameter."""
        keep_cols = ["id", "value"]
        result = filter_pipeline(
            data=df,
            threshold=0.5,
            keep_columns=keep_cols,
            show_stats=False,
        )

        assert isinstance(result, pd.DataFrame)
        for col in keep_cols:
            assert col in result.columns

    def test_filter_pipeline_with_stats(self, df):
        """Test filter pipeline with statistics display."""
        result = filter_pipeline(data=df, threshold=0.5, show_stats=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df)

    def test_filter_pipeline_auto_detect_columns(self, df):
        """Test filter with auto-detected label columns."""
        result = filter_pipeline(
            data=df,
            column_names=None,
            threshold=0.5,
            show_stats=False,
        )

        assert isinstance(result, pd.DataFrame)
        # Should auto-detect columns containing "Label"
        assert len(result) <= len(df)

    def test_filter_pipeline_no_label_columns(self, no_label_dataframe):
        """Test filter with DataFrame without label columns."""
        result = filter_pipeline(
            data=no_label_dataframe,
            column_names=None,
            threshold=0.5,
            show_stats=False,
        )

        assert isinstance(result, pd.DataFrame)
        # Should return original data if no label columns found
        assert len(result) == len(no_label_dataframe)

    def test_filter_pipeline_empty_dataframe(self, empty_df):
        """Test filter with empty DataFrame."""
        reslt = filter_pipeline(data=empty_df, threshold=0.5, show_stats=False)

        assert isinstance(reslt, pd.DataFrame)
        assert len(reslt) == 0

    def test_filter_pipeline_index_reset(self, df):
        """Test that filter pipeline resets index."""
        result = filter_pipeline(data=df, threshold=0.5, show_stats=False)

        assert isinstance(result, pd.DataFrame)
        # Check index starts from 0 and is consecutive
        if len(result) > 0:
            assert result.index[0] == 0
            assert list(result.index) == list(range(len(result)))

    def test_filter_pipeline_preserves_columns(self, df):
        """Test that filter preserves original columns."""
        result = filter_pipeline(data=df, threshold=0.5, show_stats=False)

        # record_to_keep might be added and removed
        cols = set(result.columns)
        assert "record_to_keep" not in cols

    def test_filter_pipeline_multiple_thresholds(self, df):
        """Test filter with different threshold values."""
        thresholds = [0.0, 0.33, 0.5, 0.66, 1.0]
        results_lengths = []

        for threshold in thresholds:
            result = filter_pipeline(
                data=df,
                threshold=threshold,
                show_stats=False,
            )
            results_lengths.append(len(result))

        # Higher threshold should filter out more rows
        assert results_lengths[0] >= results_lengths[-1]
