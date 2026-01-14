# AutoVQA

A Python library for automated visual question answering data generation.

## Installation

```bash
pip install autovqa
```

For development installation:

```bash
git clone https://github.com/Ddyln/AutoVQA.git
cd AutoVQA
pip install -e ".[dev]"
```

## Quick Start

```python
import json
from autovqa import eda_pipeline, filter_pipeline, balancer_pipeline

# Load your VQA data
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Step 1: Run EDA pipeline
df = eda_pipeline(data, output_dir="./reports", generate_report=True)

# Step 2: Filter low-quality records
df = filter_pipeline(df, threshold=0.5)

# Step 3: Balance the dataset
df = balancer_pipeline(df)

# Save results
df.to_csv("output.csv", index=False)
```

## Features

### Collect
Download VQA datasets and images from various sources.

```python
from autovqa.collect import download_default_data

download_default_data(output="./data")
```

### Preprocess
Image preprocessing pipeline for VQA tasks (resize, denoise, color correction, sharpening).

```python
from autovqa.preprocess.main import preprocess_image, run_pipeline

# Single image
processed = preprocess_image("image.jpg", target_size=(480, 640))

# Batch processing
run_pipeline(input_folder="./raw_images", output_folder="./processed_images")
```

### Augment
Generate VQA question-answer pairs using LLMs (e.g., Gemini).

```python
from autovqa.augment.client import AugmentClient

client = AugmentClient(service_name="gemini")
results = client.run_pipeline(
    image_folder_dir="./images",
    output_json_path="./augmented_vqa.json"
)
```

### EDA (Exploratory Data Analysis)
Analyze VQA data with cleaning, feature extraction, and report generation.

```python
from autovqa import eda_pipeline

df = eda_pipeline(
    data=data,
    output_dir="./reports",
    generate_report=True,
    aggregation_type="median"
)
```

### Filter
Filter data based on quality labels and thresholds.

```python
from autovqa import filter_pipeline

df_filtered = filter_pipeline(df, threshold=0.5, show_stats=True)
```

### Balance
Balance class distributions in your dataset.

```python
from autovqa import balancer_pipeline

df_balanced = balancer_pipeline(df_filtered, output_path="./balanced.csv")
```

## Data Format

AutoVQA expects JSON data in the following format:

```json
[
    {
        "question": "What is in the image?",
        "answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5"],
        "category": "Category name",
        "coco_url": "http://images.cocodataset.org/...",
        "index": 1
    }
]
```

## Documentation

See the [Getting Started Notebook](docs/getting_started.ipynb) for detailed usage examples.

## Development
For more details on setting up a development environment, please refer to the [Development Guide](DEV.md).

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use AutoVQA in your research, please cite:

```bibtex
```