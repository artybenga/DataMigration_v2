# Data Importer Test Suite

Last Updated: 2025-05-24 07:31:47 UTC by @artybenga

## Overview

This test suite provides comprehensive testing for the Data Importer application using pytest. It covers unit tests, integration tests, and GUI tests for all major components of the application.

## Test Structure

```
tests/
├── __init__.py
├── README.md           # This file
├── conftest.py        # Shared pytest fixtures
├── test_data/         # Test data directory
│   ├── sample.csv
│   └── sample.xlsx
├── test_data_handler.py
├── test_db_config.py
└── test_gui.py
```

## Running Tests

1. Ensure you're in the root directory of the project:
```bash
cd data_importer
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
```

3. Run the complete test suite:
```bash
pytest
```

4. Run specific test files:
```bash
pytest tests/test_data_handler.py  # Run data handler tests only
pytest tests/test_gui.py          # Run GUI tests only
pytest tests/test_db_config.py    # Run database config tests only
```

5. Run tests with coverage report:
```bash
pytest --cov=. --cov-report=html
```

## Test Components

### 1. Data Handler Tests (test_data_handler.py)
- CSV file loading
- Excel file loading (single and multiple sheets)
- NULL value handling
- File error handling
- Data type validation

### 2. Database Configuration Tests (test_db_config.py)
- Database connection testing
- Table creation
- Column name cleaning
- Error handling for database operations
- Transaction management

### 3. GUI Tests (test_gui.py)
- Window initialization
- File selection functionality
- Data preview capabilities
- Import button state management
- Logging display
- User interaction simulation

## Fixtures (conftest.py)

### Shared Test Fixtures
- `sample_csv_path`: Creates temporary CSV test file
- `sample_excel_path`: Creates temporary Excel test file with multiple sheets
- `test_logger`: Provides configured test logger
- `mock_db_config`: Mocks database configuration
- `data_handler`: Provides DataHandler instance
- `app`: Creates QApplication instance for GUI testing
- `main_window`: Provides MainWindow instance for GUI testing

## Coverage Reports

After running tests with coverage, view the HTML report:
1. Run tests with coverage: `pytest --cov=. --cov-report=html`
2. Open `htmlcov/index.html` in your browser
3. Navigate through the report to see coverage details

## Adding New Tests

When adding new tests:
1. Follow the existing file naming convention: `test_*.py`
2. Use appropriate fixtures from conftest.py
3. Add new fixtures to conftest.py if needed
4. Include docstrings explaining test purpose
5. Follow the AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_new_feature(data_handler):
    """Test description here"""
    # Arrange
    input_data = ...
    
    # Act
    result = data_handler.new_feature(input_data)
    
    # Assert
    assert result == expected_result
```

## Configuration (pytest.ini)

Located in the root directory, pytest.ini contains:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v -s --cov=. --cov-report=html
```

## Troubleshooting

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **GUI Test Failures**
   - Ensure PyQt6 is properly installed
   - Check if DISPLAY environment variable is set (Linux)
   - Run with virtual display if needed:
     ```bash
     xvfb-run pytest tests/test_gui.py
     ```

3. **Database Test Failures**
   - Verify mock configurations
   - Check connection string format
   - Ensure proper exception handling

## Maintenance

- Run tests regularly during development
- Update test data as needed
- Maintain fixture relevance
- Keep coverage above 80%
- Update dependencies regularly

## Contributing

When contributing new tests:
1. Create feature branch
2. Add tests following conventions
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## Support

For test suite issues:
1. Check troubleshooting section
2. Review test logs
3. Create detailed issue report
4. Include test environment details

## Version History

- Initial version: 2025-05-24 (by @artybenga)