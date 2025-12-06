import tomllib
from pathlib import Path

# Load config from TOML file
config_path = Path(__file__).parent / "config.toml"
with open(config_path, "rb") as f:
    config = tomllib.load(f)

NUMERIC_COLUMNS = config["columns"]["numeric"]
FEATURE_COLUMNS = config["columns"]["feature"]

# Balancer pipeline default parameters
BALANCER_PIPELINE_CONFIG = config["balancer_pipeline"]
REASON_DEPTH_WEIGHT = BALANCER_PIPELINE_CONFIG["reason_depth_weight"]
PERCENT_MIN_SAMPLES = BALANCER_PIPELINE_CONFIG["percent_min_samples"]
TOP_PERCENT = BALANCER_PIPELINE_CONFIG["top_percent"]
LIMIT_PERCENT = BALANCER_PIPELINE_CONFIG["limit_percent"]
KEEP_OUTLIERS = BALANCER_PIPELINE_CONFIG["keep_outliers"]
