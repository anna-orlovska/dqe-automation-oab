import pytest
import os

from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader


def pytest_addoption(parser):
    """Add command-line options for database connection."""
    parser.addoption(
        "--db_host",
        action="store",
        default="localhost",
        help="Database host (default: localhost)"
    )
    parser.addoption(
        "--db_port",
        action="store",
        default=5432,
        type=int,
        help="Database port (default: 5432)"
    )
    parser.addoption(
        "--db_name",
        action="store",
        required=True,
        help="Database name (required)"
    )
    parser.addoption(
        "--db_user",
        action="store",
        required=True,
        help="Database user (required)"
    )
    parser.addoption(
        "--db_password",
        action="store",
        required=True,
        help="Database password (required)"
    )
    parser.addoption(
        "--parquet_path",
        action="store",
        default="../parquet_data",
        help="Path to parquet data directory (default: ../parquet_data for dqe-automation-oab structure)"
    )


def pytest_configure(config):
    """
    Validates that all required command-line options are provided.
    Registers custom markers for test organization.
    """
    required_options = ["--db_name", "--db_user", "--db_password"]
    for option in required_options:
        if not config.getoption(option):
            pytest.fail(f"Missing required option: {option}")

    config.addinivalue_line("markers", "smoke: mark test as smoke test (quick sanity checks)")
    config.addinivalue_line("markers", "completeness: mark test as data completeness check")
    config.addinivalue_line("markers", "quality: mark test as data quality check")
    config.addinivalue_line("markers", "parquet_data: mark test as parquet data related")


@pytest.fixture(scope='session')
def db_connection(request):
    """Session-scoped fixture for PostgreSQL database connection."""
    db_host = request.config.getoption("--db_host")
    db_port = request.config.getoption("--db_port")
    db_name = request.config.getoption("--db_name")
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")

    try:
        connector = PostgresConnectorContextManager(
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password
        )
        connection = connector.__enter__()
        yield connection
        connector.__exit__(None, None, None)
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {str(e)}")


@pytest.fixture(scope='session')
def parquet_reader():
    """Session-scoped fixture for Parquet file reader."""
    return ParquetReader()


@pytest.fixture(scope='session')
def data_quality_library():
    """Session-scoped fixture for DataQualityLibrary."""
    return DataQualityLibrary()


@pytest.fixture(scope='session')
def parquet_path(request):
    """Session-scoped fixture for parquet data path."""
    return request.config.getoption("--parquet_path")