# Test Suite

Comprehensive test suite for the Packer VexxHost Bastion Action.

## Running Tests

### Install dependencies
```bash
pip install -e ".[test]"
```

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_action_yaml.py
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_action_yaml.py` - Tests for action.yaml structure and configuration
- `test_workflows.py` - Tests for example workflow files

## Coverage Target

Target coverage: 80%+

Coverage reports are generated in:
- Terminal output
- `htmlcov/` directory (HTML report)
- `coverage.xml` (for CI/CD)
