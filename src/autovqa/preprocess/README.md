# Image Preprocessing Pipeline

A comprehensive guide to running the image preprocessing pipeline for AutoVQA.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Pipeline](#running-the-pipeline)
4. [CLI Options](#cli-options)
5. [Usage Examples](#usage-examples)
6. [Processing Pipeline](#processing-pipeline)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

- Python 3.8+
- Poetry (recommended) or pip

### Using Poetry
- Navigate to your project
```bash
poetry install
```

Dependencies will be automatically installed from `pyproject.toml`:
- `opencv-python` - Image processing
- `numpy` - Numerical computing
- `appdirs` - Path management

### Using pip

```bash
pip install opencv-python numpy appdirs
```

---

## Configuration (Reference)

### 1. Default Configuration (from config.py)

Configuration file location: `src/autovqa/config/config.py`

**Default Paths:**

- **Linux**: `~/.local/share/your_autovqa_package/images/`
- **macOS**: `~/Library/Application Support/your_autovqa_package/images/`
- **Windows**: `C:\Users\<username>\AppData\Local\your_autovqa_package\images\`

**Default Folders:**

```
~/.local/share/your_autovqa_package/images/
├── raw_images_from_urls/          # Input images (default)
└── preprocessed_url_images/       # Output images (default)
```

### 2. Change PACKAGE_NAME (Optional)

Edit `src/autovqa/config/config.py`:

```python
PACKAGE_NAME = "your_autovqa_package"  # Change to your package name
```

Example:
```python
PACKAGE_NAME = "my_vqa_project"
```

### 3. Override Default Path with Environment Variable (Optional)

**On Linux/macOS:**

```bash
export YOURPKG_BASE_DIR="/path/to/your/data"
poetry run python -m autovqa.preprocess.main
```

**On Windows (PowerShell):**

```powershell
$env:YOURPKG_BASE_DIR = "C:\path\to\your\data"
poetry run python -m autovqa.preprocess.main
```

---

## Running the Pipeline

### Method 1: Run with Custom Parameters (Recommended)

```bash
poetry run python -m autovqa.preprocess.main \
  --input /path/to/input/images \
  --output /path/to/output/images
```

### Method 2: Run with Default Configuration

```bash
poetry run python -m autovqa.preprocess.main
```

### Method 3: Run from Python Script

```python
from autovqa.preprocess.main import run_pipeline

# Run with custom parameters
run_pipeline(
    input_folder="/path/to/input",
    output_folder="/path/to/output",
    do_normalize=False
)

# Or run with defaults
run_pipeline()
```

### Method 4: Process Individual Images

```python
import cv2
from autovqa.preprocess.main import preprocess_image

# Process a single image
processed = preprocess_image(
    image_path="path/to/image.jpg",
    target_size=(480, 640),
    do_normalize=False
)

# Save result
cv2.imwrite("output.jpg", processed)
```

---

## CLI Options

```bash
poetry run python -m autovqa.preprocess.main --help
```

**Available Options:**

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--input` | Input folder with raw images | config default | `--input /home/luminous/images` |
| `--output` | Output folder for processed images | config default | `--output /home/luminous/output` |
| `--normalize` | Normalize images to [0, 1] range | None (default uint8) | `--normalize` |
| `--help` | Show help message | - | `--help` |

---

## Usage Examples

### Example 1: Process Images from Custom Folder

```bash
poetry run python -m autovqa.preprocess.main \
  --input /home/luminous/input_img \
  --output /home/luminous/output_img
```

**Output:**

```
Scanned 1/1 images
Most common size: (533x800) - 1 images
Using target size: (533, 800)
Found 2 images in /home/luminous/input_img
Processing 1/2: image1.jpg
Finished: image1.jpg
Processing 2/2: image2.jpg
Finished: image2.jpg
Preprocessed images saved to: /home/luminous/output_img
```

### Example 2: Process with Normalization

```bash
poetry run python -m autovqa.preprocess.main \
  --input /home/luminous/input_img \
  --output /home/luminous/output_img \
  --normalize
```

### Example 3: Change Only Output Folder

```bash
poetry run python -m autovqa.preprocess.main \
  --output /custom/output/path
```

(Input folder will use default from config)

### Example 4: Using Environment Variable

```bash
export YOURPKG_BASE_DIR="/mnt/data"
poetry run python -m autovqa.preprocess.main --input /mnt/data/images/raw
```

---

## Processing Pipeline

The preprocessing pipeline performs the following steps on each image:

```
Input Image (BGR)
    |
    v
1. Resize (maintain aspect ratio)
    |
    v
2. Pad (align to exact size)
    |
    v
3. Denoise (noise reduction)
    |
    v
4. Color Correction (CLAHE - enhance contrast)
    |
    v
5. Sharpening (Unsharp Mask)
    |
    v
6. Optional Normalization (0-1 range)
    |
    v
Output Image (uint8 or float32)
```

### Step Details:

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `resize_image()` | Resize to fit target_size while maintaining aspect ratio |
| 2 | `pad_image()` | Pad image to exact size (480x640) |
| 3 | `denoise_image()` | Reduce noise using fastNlMeansDenoisingColored |
| 4 | `color_correction()` | Apply CLAHE on L-channel in LAB colorspace |
| 5 | `unsharp_mask()` | Sharpen image edges |
| 6 | `normalize_image()` | Optional: normalize to [0, 1] |

---

## Module Details

### image/resize.py

- `resize_image()`: Resize image to fit target_size (480, 640) while preserving aspect ratio
- `pad_image()`: Pad image with black borders to reach exact target_size

**Default Size:**
```python
target_size = (480, 640)  # (height, width)
```

### image/denoise.py

- `denoise_image()`: Uses `cv2.fastNlMeansDenoisingColored`
  - `h=3` (filter strength)
  - `templateWindowSize=7`
  - `searchWindowSize=21`

### image/color_correction.py

- `color_correction()`: Apply CLAHE on L-channel
  - Convert BGR to LAB
  - Apply CLAHE with `clipLimit=2.0`, `tileGridSize=(8, 8)`
  - Convert LAB back to BGR

### image/sharpening.py

- `unsharp_mask()`: Unsharp Mask sharpening
  - `amount=1.5` (sharpening intensity)
  - Uses Gaussian blur with `sigmaX=2`

### image/normalize.py

- `normalize_image()`: Normalize pixels to [0, 1]
- `normalize_batch()`: Normalize a batch of images

---

## Troubleshooting

### Error: "No module named 'autovqa'"

**Cause**: Package not installed or wrong working directory

**Solution**:
```bash
cd /home/luminous/HCMUS/AutoVQA
poetry install
```

### Error: "Input folder does not exist"

**Cause**: Input folder path is incorrect

**Solution**:
```bash
# Check folder
ls -la /path/to/input

# Create folder if needed
mkdir -p /path/to/input
```

### Error: "No images found in input folder"

**Cause**: No images in input folder or wrong file format

**Solution**:
- Check file format: `.jpg`, `.jpeg`, `.png`
- Verify case sensitivity

```bash
# Check images
ls -la /path/to/input/*.{jpg,jpeg,png}
```

### Error: "Cannot read: <image_path>"

**Cause**: Image file is corrupted or not a valid image

**Solution**:
```bash
# Check file type
file /path/to/image.jpg

# Try reading with Python
python -c "import cv2; img = cv2.imread('/path/to/image.jpg'); print(f'Shape: {img.shape if img is not None else \"Error\"}')"
```

### Output folder already exists, images are skipped

**Behavior**: If output image already exists, pipeline skips it to avoid reprocessing

**Solution** (if you want to reprocess):
```bash
# Delete output folder
rm -rf /path/to/output

# Or use a different output folder
poetry run python -m autovqa.preprocess.main \
  --input /path/to/input \
  --output /path/to/new/output
```

### Images not saving to output folder

**Cause**: Permission issues or invalid output path

**Solution**:
```bash
# Create output folder with proper permissions
mkdir -p /path/to/output
chmod 755 /path/to/output

# Try again
poetry run python -m autovqa.preprocess.main \
  --input /path/to/input \
  --output /path/to/output
```

---

## Performance

**Processing speed** depends on:
- Image resolution
- Number of images
- Enabled features (denoise, color correction, sharpening)

**Estimated times** (with typical CPU):
- 1 image (480x640): 0.5-1s
- 100 images: 50-100s

---

## Additional Resources

- OpenCV Documentation: https://docs.opencv.org/
- NumPy Documentation: https://numpy.org/
- Poetry Documentation: https://python-poetry.org/

---

## Quick Start

```bash
# 1. Install
cd /home/luminous/HCMUS/AutoVQA
poetry install

# 2. Run pipeline
poetry run python -m autovqa.preprocess.main \
  --input /home/luminous/input_img \
  --output /home/luminous/output_img

# 3. Check results
ls -la /home/luminous/output_img
```

---

For more help:

```bash
poetry run python -m autovqa.preprocess.main --help
```
