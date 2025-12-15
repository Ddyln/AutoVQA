"""Integration tests for combined EDA, Filter, and Balancer pipelines."""

import json

import pandas as pd
import pytest

from autovqa import balancer_pipeline, eda_pipeline, filter_pipeline

# Path to the actual test data
DATA_PATH = (
    r"C:\Users\ADMIN\.cache\kagglehub\datasets\nguynrichard"
    r"\auto-vivqa\versions\1\text\text\combined_evaluation_data.json"
)


@pytest.fixture
def data():
    """Load real VQA data from the specified path."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        pytest.skip(f"Data file not found at {DATA_PATH}")
    except json.JSONDecodeError:
        pytest.skip(f"Invalid JSON in data file at {DATA_PATH}")


class TestPipelineIntegration:
    """Integration tests for the complete pipeline workflow."""

    def test_full_pipeline_with_real_data(self, data, tmp_path):
        """Test complete pipeline: EDA -> Filter -> Balancer."""
        # Step 1: EDA Pipeline
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        initial_rows = len(df)

        # Step 2: Filter Pipeline
        df = filter_pipeline(df, threshold=0.5, show_stats=False)

        assert isinstance(df, pd.DataFrame)
        assert len(df) <= initial_rows
        filtered_rows = len(df)

        # Step 3: Balancer Pipeline
        df = balancer_pipeline(df_raw=df)

        assert isinstance(df, pd.DataFrame)
        assert len(df) <= filtered_rows
        final_rows = len(df)

        # Verify data integrity
        assert final_rows > 0
        assert isinstance(df.index, pd.RangeIndex)

    def test_pipeline_data_reduction(self, data, tmp_path):
        """Test that pipeline reduces data appropriately."""
        initial_count = len(data)

        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        after_eda = len(df)

        df = filter_pipeline(df, threshold=0.5, show_stats=False)
        after_filter = len(df)

        df = balancer_pipeline(df_raw=df)
        after_balance = len(df)

        # Each stage should reduce or maintain data count
        assert after_eda <= initial_count
        assert after_filter <= after_eda
        assert after_balance <= after_filter

    def test_pipeline_with_low_threshold(self, data, tmp_path):
        """Test pipeline with low filter threshold."""
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        df = filter_pipeline(df, threshold=0.3, show_stats=False)
        df = balancer_pipeline(df_raw=df)

        assert isinstance(df, pd.DataFrame)
        # Low threshold should keep more data
        assert len(df) > 0

    def test_pipeline_with_high_threshold(self, data, tmp_path):
        """Test pipeline with high filter threshold."""
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        df = filter_pipeline(df, threshold=0.9, show_stats=False)

        if len(df) > 0:
            df = balancer_pipeline(df_raw=df)
            assert isinstance(df, pd.DataFrame)
        else:
            # High threshold might filter out all data
            assert len(df) == 0

    def test_pipeline_output_to_file(self, data, tmp_path):
        """Test pipeline with file output."""
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=True,
        )
        df = filter_pipeline(df, threshold=0.5, show_stats=False)

        out_file = tmp_path / "balanced_result.csv"
        df = balancer_pipeline(df_raw=df, output_path=str(out_file))

        assert isinstance(df, pd.DataFrame)
        assert out_file.exists()

    def test_pipeline_returns_dataframe_each_step(self, data, tmp_path):
        """Test that each pipeline step returns a DataFrame."""
        # Step 1
        result1 = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        assert isinstance(result1, pd.DataFrame)

        # Step 2
        result2 = filter_pipeline(result1, threshold=0.5, show_stats=False)
        assert isinstance(result2, pd.DataFrame)

        # Step 3
        result3 = balancer_pipeline(df_raw=result2)
        assert isinstance(result3, pd.DataFrame)

    def test_pipeline_with_minimal_balancer_settings(self, data, tmp_path):
        """Test pipeline with minimal balancer settings."""
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        df = filter_pipeline(df, threshold=0.5, show_stats=False)
        df = balancer_pipeline(
            df_raw=df,
            percent_min_samples=0.05,
            top_percent=0.7,
            limit_percent=20,
        )

        assert isinstance(df, pd.DataFrame)

    def test_pipeline_sequential_execution(self, data, tmp_path):
        """Test sequential execution matches expected behavior."""
        # Execute pipeline
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
        )
        df = filter_pipeline(df, threshold=0.5, show_stats=False)
        df = balancer_pipeline(df_raw=df)

        # Verify final result
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_pipeline_with_real_data_custom_params(self, data, tmp_path):
        """Test pipeline with real data and custom parameters."""
        df = eda_pipeline(
            data=data,
            output_dir=str(tmp_path),
            generate_report=False,
            aggregation_type="median",
        )
        df = filter_pipeline(df, threshold=0.6, show_stats=True)
        df = balancer_pipeline(
            df_raw=df,
            reason_depth_weight=4,
            percent_min_samples=0.01,
            top_percent=0.9,
            limit_percent=10,
            keep_outliers=True,
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_pipeline_idempotency(self, data, tmp_path):
        """Test pipeline produces consistent results."""
        # Run pipeline twice
        df1 = eda_pipeline(
            data=data,
            output_dir=str(tmp_path / "run1"),
            generate_report=False,
        )
        df1 = filter_pipeline(df1, threshold=0.5, show_stats=False)
        df1 = balancer_pipeline(df_raw=df1)

        df2 = eda_pipeline(
            data=data,
            output_dir=str(tmp_path / "run2"),
            generate_report=False,
        )
        df2 = filter_pipeline(df2, threshold=0.5, show_stats=False)
        df2 = balancer_pipeline(df_raw=df2)

        # Results should be similar (same shape)
        assert len(df1) == len(df2)
        assert list(df1.columns) == list(df2.columns)
