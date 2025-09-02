# Developer Guide

This document provides instructions for developers working on the taskflow-mcp project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourname/taskflow-mcp.git
   cd taskflow-mcp
   ```

2. Install development dependencies:
   ```bash
   uv sync --frozen --all-extras --dev
   ```

3. Set up pre-commit hooks:
```bash
uv tool install pre-commit --with pre-commit-uv --force-reinstall
```

## Testing

### Running Tests

The project uses pytest for testing with comprehensive coverage reporting.

#### Quick Test Run
```bash
# Run all tests with coverage
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_server.py -v

# Run tests matching a pattern
uv run pytest -k "test_create" -v
```

#### Using the Test Runner Script
```bash
# Run the custom test runner (includes coverage and HTML report)
python run_tests.py
```

#### Test Coverage
```bash
# Generate coverage report
uv run pytest --cov=taskflow_mcp --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=taskflow_mcp --cov-report=html:htmlcov
```

#### Test Categories
Tests are organized into categories using pytest markers:

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run only fast tests (exclude slow tests)
uv run pytest -m "not slow"
```

### Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest configuration and fixtures
├── test_server.py           # Unit tests for server methods
├── test_main.py             # Tests for main entry point
└── test_integration.py      # End-to-end workflow tests
```

### Writing Tests

#### Test Fixtures
The project provides several useful fixtures in `conftest.py`:

- `temp_dir`: Creates a temporary directory for testing
- `mock_base_dir`: Creates a mock `.tasks` directory
- `sample_checklist`: Sample checklist data for testing
- `sample_investigation_content`: Sample investigation content
- `sample_solution_plan_content`: Sample solution plan content

#### Example Test
```python
def test_create_investigation_basic(self, temp_dir, sample_investigation_content):
    """Test creating an investigation file with default content."""
    with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
        task_id = "test-task"
        result = create_investigation(task_id)
        
        expected_path = task_path(task_id, "INVESTIGATION.md")
        assert os.path.exists(expected_path)
        assert result == f"Created {expected_path}"
```

#### Test Guidelines

1. **Use fixtures** for common test data and setup
2. **Mock filesystem operations** using `patch` to avoid affecting real files
3. **Test both success and failure cases**
4. **Include docstrings** explaining what each test does
5. **Use descriptive test names** that explain the scenario
6. **Test edge cases** like empty inputs, missing files, invalid data

### Test Coverage

The project aims for high test coverage. Current coverage targets:

- **Minimum coverage**: 80% (configured in `pytest.ini`)
- **Target coverage**: 90%+

View coverage reports:
```bash
# Terminal report
uv run pytest --cov=taskflow_mcp --cov-report=term-missing

# HTML report (opens in browser)
uv run pytest --cov=taskflow_mcp --cov-report=html:htmlcov
open htmlcov/index.html
```

## Code Quality

### Linting and Formatting

The project uses several tools for code quality:

```bash
# Format code with black
uv run black taskflow_mcp/ tests/

# Sort imports with isort
uv run isort taskflow_mcp/ tests/

# Lint with flake8
uv run flake8 taskflow_mcp/ tests/

# Type checking with mypy
uv run mypy taskflow_mcp/
```

### Pre-commit Hooks (Optional)

To set up pre-commit hooks:

```bash
# Install pre-commit
uv add --dev pre-commit

# Install hooks
uv run pre-commit install
```

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run tests** to ensure nothing is broken:
   ```bash
   uv run pytest
   ```

4. **Check code quality**:
   ```bash
   uv run black taskflow_mcp/ tests/
   uv run flake8 taskflow_mcp/ tests/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

### Testing New Features

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure all tests pass**
3. **Add integration tests** for complex workflows
4. **Update documentation** if needed

### Debugging Tests

For debugging failing tests:

```bash
# Run with verbose output and stop on first failure
uv run pytest -xvs

# Run specific test with debugging
uv run pytest tests/test_server.py::TestCreateInvestigation::test_create_investigation_basic -xvs

# Run with pdb debugger
uv run pytest --pdb
```

## Project Structure

```
taskflow-mcp/
├── taskflow_mcp/           # Main package
│   ├── __init__.py        # Package initialization
│   └── server.py          # MCP server implementation
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   ├── test_server.py     # Server tests
│   ├── test_main.py       # Main entry point tests
│   └── test_integration.py # Integration tests
├── pyproject.toml         # Project configuration
├── pytest.ini            # Pytest configuration
├── run_tests.py          # Test runner script
├── README.md             # User documentation
└── DEVELOPER.md          # This file
```

## Troubleshooting

### Common Issues

#### Tests Failing Due to Import Errors
```bash
# Ensure you're in the project root
cd /path/to/taskflow-mcp

# Install dependencies
uv sync --extra dev
```

#### Coverage Not Working
```bash
# Install coverage dependencies
uv add --dev pytest-cov

# Run with explicit coverage
uv run pytest --cov=taskflow_mcp
```

#### Permission Errors on macOS/Linux
```bash
# Make test runner executable
chmod +x run_tests.py
```

### Getting Help

- Check the test output for specific error messages
- Look at existing tests for examples
- Review the pytest documentation: https://docs.pytest.org/
- Check the project's GitHub issues for known problems

## Contributing

When contributing to the project:

1. **Follow the existing code style**
2. **Add tests for new functionality**
3. **Update documentation** as needed
4. **Ensure all tests pass** before submitting
5. **Write clear commit messages**

### Pull Request Checklist

- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] No linting errors
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
