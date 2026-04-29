# Development Guide

Guidelines for developing and extending the PyTest DQ Framework.

## Table of Contents

- [Project Structure](#project-structure)
- [Adding New Tests](#adding-new-tests)
- [Adding New Data Quality Checks](#adding-new-data-quality-checks)
- [Best Practices](#best-practices)
- [Code Style](#code-style)
- [Testing Locally](#testing-locally)
- [Debugging](#debugging)

## Project Structure

```
PyTest DQ Framework/
├── src/
│   ├── connectors/
│   │   ├── postgres/
│   │   │   └── postgres_connector.py      # PostgreSQL connection manager
│   │   └── file_system/
│   │       └── parquet_reader.py          # Parquet file reader
│   └── data_quality/
│       └── data_quality_validation_library.py  # DQ validation methods
├── tests/
│   ├── conftest.py                       # pytest configuration and fixtures
│   ├── test_examples.py                  # Example test patterns
│   └── dq checks/
│       └── parquet_files/               # Test modules by category
│           ├── test_facility_name_*.py
│           ├── test_facility_type_*.py
│           ├── test_smoke_*.py
│           └── test_data_quality_*.py
├── pytest.ini                            # pytest configuration
├── requirements.txt                      # Dependencies
└── Jenkinsfile                          # Jenkins pipeline
```

## Adding New Tests

### 1. Create Test File

Create a new file in `tests/dq checks/parquet_files/` following the naming convention:

```bash
touch "PyTest DQ Framework/tests/dq checks/parquet_files/test_your_feature.py"
```

### 2. Test File Template

```python
"""
Description: Data Quality checks for [feature description].
Validates [what is being validated].
Requirement(s): TICKET-XXXX
Author(s): Your Name
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    """Fetch source data from PostgreSQL."""
    sql = """
    SELECT
        column1,
        column2,
        column3
    FROM your_table
    WHERE conditions
    ORDER BY column1
    """
    return db_connection.get_data_sql(sql)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    """Load target data from Parquet."""
    return parquet_reader.process('parquet_data/your_dataset')


class TestSmoke:
    """Smoke tests - quick structure validation."""

    @pytest.mark.smoke
    @pytest.mark.parquet_data
    def test_source_not_empty(self, source_data, data_quality_library):
        """Verify source dataset is not empty."""
        data_quality_library.check_dataset_is_not_empty(source_data)

    # Add more smoke tests...


class TestCompleteness:
    """Completeness tests - verify no missing values."""

    @pytest.mark.completeness
    @pytest.mark.parquet_data
    def test_source_no_nulls(self, source_data, data_quality_library):
        """Verify source has no null values."""
        data_quality_library.check_data_completeness(source_data)

    # Add more completeness tests...


class TestQuality:
    """Quality tests - advanced DQ checks."""

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_source_no_duplicates(self, source_data, data_quality_library):
        """Verify source has no duplicates."""
        data_quality_library.check_duplicates(source_data, column_names=['id'])

    # Add more quality tests...
```

### 3. Test Markers

Use markers to organize and filter tests:

| Marker | Usage |
|--------|-------|
| `@pytest.mark.smoke` | Quick sanity checks |
| `@pytest.mark.completeness` | Null value checks |
| `@pytest.mark.quality` | Advanced DQ checks |
| `@pytest.mark.parquet_data` | Tests related to Parquet files |

### 4. Running New Tests

```bash
# Run your new test file
pytest tests/dq\ checks/parquet_files/test_your_feature.py \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase

# Run with specific marker
pytest tests -m "smoke and parquet_data" \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

## Adding New Data Quality Checks

### 1. Extend DataQualityLibrary

Edit `src/data_quality/data_quality_validation_library.py`:

```python
@staticmethod
def check_my_custom_check(df: pd.DataFrame, **kwargs) -> None:
    """
    Description of what this check does.

    Args:
        df: DataFrame to check
        **kwargs: Additional parameters

    Raises:
        AssertionError: If check fails
    """
    # Your validation logic here
    result = ...
    assert result, f"Check failed: {message}"
```

### 2. Use in Tests

```python
def test_my_custom_check(self, source_data, data_quality_library):
    """Test description."""
    data_quality_library.check_my_custom_check(source_data)
```

### 3. Example: Custom Uniqueness Check

```python
@staticmethod
def check_uniqueness(df: pd.DataFrame, column_names: list) -> None:
    """
    Verify that column combinations are unique.

    Args:
        df: DataFrame to check
        column_names: List of columns to check for uniqueness

    Raises:
        AssertionError: If duplicates found
    """
    duplicates = df.duplicated(subset=column_names).sum()
    assert duplicates == 0, (
        f"Column combination {column_names} has {duplicates} duplicate(s)"
    )
```

## Best Practices

### 1. Test Organization

- **One test file per logical data entity** (e.g., `test_facility_name_*.py`)
- **Organize by test type**: Smoke → Completeness → Quality
- **Group related tests in classes**

### 2. Fixtures

- **Use module scope** for expensive operations (DB queries, file reads)
- **Name fixtures clearly** (`source_data`, `target_data`)
- **Document fixtures** with docstrings

```python
@pytest.fixture(scope='module')
def source_data(db_connection):
    """Fetch [what data] from [where]."""
    # ...
```

### 3. Assertions

- **Use library methods** instead of raw assertions
- **Provide clear error messages**:

```python
# Good
assert not missing, f"Missing columns in source: {missing}"

# Bad
assert False, "error"
```

### 4. SQL Queries

- **Comment complex queries**:

```python
query = """
    SELECT
        facility_type,
        visit_date,
        -- Calculate minimum time spent per facility type and date
        MIN(time_spent) as min_time_spent
    FROM patient_treatment
    WHERE facility_type IS NOT NULL
    GROUP BY facility_type, visit_date
"""
```

- **Order results for consistency**:

```python
query = """
    ...
    ORDER BY facility_type, visit_date  -- Important for comparison
"""
```

### 5. Error Messages

- **Be specific** about what failed:

```python
# Good
assert len(missing) == 0, f"Found {len(missing)} invalid facility types: {missing}"

# Bad
assert len(missing) == 0, "Check failed"
```

### 6. Documentation

- **Add docstrings to all tests**:

```python
def test_name(self, fixture):
    """Test description - what is being validated and why."""
    # ...
```

- **Include Requirement IDs**:

```python
"""
Description: Validates facility type distribution.
Requirement(s): FRAMEWORK-014, JIRA-5678
Author(s): Your Name
"""
```

## Code Style

### Python Style Guide

Follow PEP 8 conventions:

```bash
# Check style (if flake8 installed)
flake8 "PyTest DQ Framework/src" "PyTest DQ Framework/tests"

# Auto-format (if black installed)
black "PyTest DQ Framework/src" "PyTest DQ Framework/tests"
```

### Naming Conventions

```python
# Good
def test_patient_id_is_positive(self):
    """Clear, descriptive test name."""
    pass

source_data = db_connection.get_data_sql(query)  # Clear variable names

# Bad
def test_1(self):
    """What does this test?"""
    pass

data = db_connection.get_data_sql(query)  # Too generic
```

### Imports

```python
# Good
import pytest
import pandas as pd
from connectors.postgres.postgres_connector import PostgresConnectorContextManager

# Bad
from connectors.postgres.postgres_connector import *  # Avoid wildcard imports
import *  # Never do this
```

## Testing Locally

### 1. Run Specific Test

```bash
cd "PyTest DQ Framework"
pytest tests/dq\ checks/parquet_files/test_your_feature.py::TestClassName::test_method_name \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### 2. Run with Verbose Output

```bash
pytest tests -v -s \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

Options:
- `-v`: Verbose output
- `-s`: Show print statements
- `-x`: Stop on first failure
- `--tb=long`: Detailed traceback

### 3. Generate Report While Testing

```bash
pytest tests --html=report.html --self-contained-html \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

## Debugging

### 1. Print Debug Information

```python
def test_something(self, source_data):
    """Test with debug output."""
    print("\nDataFrame shape:", source_data.shape)
    print("Columns:", source_data.columns.tolist())
    print("\nFirst few rows:")
    print(source_data.head())
    
    # Your test code...
```

Run with `-s` to see output:
```bash
pytest test_file.py -s --db_host=... --db_user=... --db_password=... --db_name=...
```

### 2. Use pytest.set_trace()

```python
def test_something(self, source_data):
    """Test with breakpoint."""
    pytest.set_trace()  # Will drop to debugger here
    # Your test code...
```

### 3. Inspect DataFrame

```python
def test_something(self, source_data, data_quality_library):
    """Inspect data before assertion."""
    print("\nData info:")
    print(source_data.info())
    print("\nData description:")
    print(source_data.describe())
    print("\nNull counts:")
    print(source_data.isnull().sum())
    
    data_quality_library.check_data_completeness(source_data)
```

### 4. SQL Debugging

```python
@pytest.fixture(scope='module')
def source_data(db_connection):
    """Fetch data with debugging."""
    query = """
        SELECT * FROM table LIMIT 10
    """
    print(f"\nExecuting query:\n{query}")
    result = db_connection.get_data_sql(query)
    print(f"\nReturned {len(result)} rows")
    print(f"Columns: {result.columns.tolist()}")
    return result
```

### 5. Check Database Directly

```bash
# From local machine
psql -h localhost -p 5434 -U myuser -d mydatabase

# From Docker container
docker exec -it postgres psql -U myuser -d mydatabase

# Run specific query
psql -h localhost -p 5434 -U myuser -d mydatabase -c "SELECT COUNT(*) FROM table;"
```

## Common Issues and Solutions

### Issue: "Database connection failed"
```bash
# Check container status
docker ps | grep postgres

# Check PostgreSQL logs
docker logs postgres

# Test connection manually
psql -h localhost -p 5434 -U myuser -d mydatabase
```

### Issue: "Parquet file not found"
```bash
# Check if parquet_data directory exists
ls -la parquet_data/

# Verify file paths in test fixtures
find parquet_data/ -name "*.parquet"
```

### Issue: "Module not found"
```bash
# Verify source is marked as source root in IDE
# Verify imports use correct path:
from connectors.postgres.postgres_connector import PostgresConnectorContextManager
# NOT: from src.connectors.postgres...
```

### Issue: "Test timeout"
```bash
# Run with longer timeout
pytest tests --timeout=600 \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

## Git Workflow

### Create Feature Branch

```bash
git checkout -b feature/my-new-tests
```

### Commit Changes

```bash
git add "PyTest DQ Framework/tests/dq checks/parquet_files/test_new_feature.py"
git commit -m "Add tests for [feature description]"
```

### Push and Create PR

```bash
git push origin feature/my-new-tests
# Then create PR on GitHub
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/documentation/)
- [PEP 8 Style Guide](https://pep8.org/)
