import pytest
import pandas as pd
import os
from pathlib import Path


# Fixture to read the CSV file
@pytest.fixture(scope="session")
def csv_data():
    # file_path = "C:\\Users\\AnnaOrlovska\\Documents\\OrlAnn\\Epam\\Automation_DQA\\dqe-automation-oab\\PyTest_Introduction\\src\\data\\data.csv"

    project_root = Path(__file__).resolve().parent.parent  # .../PyTest_Introduction
    file_path = project_root / "src" / "data" / "data.csv"

    if not file_path.exists():
        pytest.fail(f"CRITICAL: Data file not found at {file_path}")

    return pd.read_csv(file_path)


# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def validate_schema(csv_data):
    expected_columns = {'id', 'name', 'age', 'email', 'is_active'}
    actual_columns = set(csv_data.columns)
    missing_columns = expected_columns.difference(actual_columns)
    extra_columns = actual_columns.difference(expected_columns)
    errors = []
    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
    if extra_columns:
        errors.append(f"Extra columns: {extra_columns}")
    if errors:
        pytest.fail("\n".join(errors))
    return csv_data

# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        if not list(item.iter_markers()):
            unmarked_marker = pytest.mark.unmarked
            item.add_marker(unmarked_marker)