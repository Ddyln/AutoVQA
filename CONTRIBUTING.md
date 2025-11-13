# Contributing to AutoVQA

We welcome contributions to AutoVQA! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/Ddyln/AutoVQA.git
   cd autovqa
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests

3. Run the test suite:
   ```bash
   pytest
   ```

4. Check code formatting:
   ```bash
   black src tests
   isort src tests
   ```

5. Run type checking:
   ```bash
   mypy src
   ```

6. Run linting:
   ```bash
   flake8 src tests
   ```

7. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your commit message"
   ```

8. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

9. Create a pull request on GitHub

## Code Style

- We use [Black](https://black.readthedocs.io/) for code formatting
- We use [isort](https://pycqa.github.io/isort/) for import sorting
- We use [flake8](https://flake8.pycqa.org/) for linting
- We use [mypy](http://mypy-lang.org/) for type checking

## Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage
- Use descriptive test names and docstrings

## Documentation

- Add docstrings to all public functions and classes
- Update the README.md if needed
- Add examples for new features

## Pull Request Guidelines

- Include a clear description of the changes
- Reference any related issues
- Ensure all CI checks pass
- Keep pull requests focused and atomic

## Reporting Issues

- Use the GitHub issue tracker
- Provide a clear description of the issue
- Include steps to reproduce
- Provide relevant environment information

## Questions?

If you have questions about contributing, please open an issue or reach out to the maintainers.

Thank you for contributing to AutoVQA!
