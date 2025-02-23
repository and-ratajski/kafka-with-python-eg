# Examples of Kafka + Python Integration

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
```bash
# Create virtual environment using venv
python -m venv .venv

# Activate it on:
# Linux/macOS:
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

3. Install the package with development dependencies:
```bash
pip install -e ".[test]"
```

## Development

### Managing Dependencies

- Add new runtime dependency:
  1. Add package to `dependencies` in `pyproject.toml`
  2. Run `pip install -e .`

- Add new development dependency:
  1. Add package to `[project.optional-dependencies]` under `test` in `pyproject.toml` 
  2. Run `pip install -e ".[test]"`

- Remove dependency:
  1. Remove package from `pyproject.toml`
  2. Run `pip uninstall package-name`

### Code Quality Tools

The project uses the following tools to maintain code quality:

- **Black**: Code formatter that enforces a consistent style
  ```bash
  black .  # Format all Python files
  ```

- **isort**: Import statement organizer
  ```bash
  isort .  # Sort imports in all Python files
  ```

- **flake8**: Style guide enforcer
  ```bash
  flake8  # Check code style
  ```

All tools are configured in `pyproject.toml` with 120 characters line length.

### Testing

The project uses pytest for testing. Tests are located in the `tests/` directory.

Types of tests:
- **Unit tests**: Test individual components in isolation
  - Example: Testing a single function's input/output
  - Located in `tests/unit/`

- **Integration tests**: Test multiple components working together
  - Example: Testing matrix operations chain
  - Located in `tests/integration/`

Running tests:

```bash
pytest  # Run all tests
pytest tests/unit/  # Run only unit tests
pytest -k "test_name"  # Run specific test
```

## See Also

- [Contributing Guidelines](CONTRIBUTING.md)
