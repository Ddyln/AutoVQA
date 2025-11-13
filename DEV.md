# AutoVQA Development Guide

This guide provides instructions for setting up the development environment and contributing to the AutoVQA project.

## Quick Start

### Prerequisites
- Python 3.10
- Git
- (Optional but recommended) Conda or virtual environment manager

### 1. Clone the Repository
```bash
git clone https://github.com/Ddyln/AutoVQA.git
cd AutoVQA
```

### 2. Set up Development Environment

#### Option A: Using Conda (Recommended)
```bash
# Create conda environment
conda create -n autovqa python=3.10
conda activate autovqa

# Install in development mode
pip install -e ".[dev]"
```

#### Option B: Using venv
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"
```

### 3. Install Pre-commit Hooks
```bash
pre-commit install
```

## Development Workflow

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Running Code Quality Checks

Git automatically runs these tools on each commit via pre-commit hooks but you can also run them manually:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Or run individual tools
black src tests
isort src tests
flake8 src tests
mypy src
```

### Unit Testing
- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Include docstrings for complex test cases
- Use fixtures from `conftest.py` when possible

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest --cov=src/autovqa --cov-report=html tests/

# Run specific test file
pytest tests/test_import.py

# Run with verbose output
pytest -v tests/
```

## Version Management
The project uses dynamic versioning from `src/autovqa/version.py`:

```python
# To update version, edit src/autovqa/version.py
__version__ = "0.1.0"
```

## Code Style Guidelines

### Python Code Style
- Follow **PEP 8** style guide
- Use type hints for all function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Maximum line length: 88 characters (Black default)

### Docstring Format
```python
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers.

    Args:
        a: First number.
        b: Second number.

    Returns:
        Product of a and b.

    Example:
        >>> multiply(2, 3) # Returns 6
    """
    return a * b
```

### Import Organization
```python
# Standard library imports
import os
from pathlib import Path

# Third-party imports
import numpy as np
from PIL import Image

# Local imports
import autovqa
```

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
