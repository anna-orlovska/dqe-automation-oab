"""
Description: Smoke tests for basic data structure validation.
Quick sanity checks to verify data structure and connectivity.
Requirement(s): FRAMEWORK-013
Author(s): QA Team
"""

import pytest


@pytest.fixture(scope='module')
def patient_treatment_data(db_connection):
    """Fetch basic patient treatment data."""
    query = "SELECT * FROM patient_treatment LIMIT 100"
    return db_connection.get_data_sql(query)


class TestDatabaseConnectivity:
    """Tests for database connectivity and basic operations."""

    @pytest.mark.smoke
    def test_database_connection_established(self, db_connection):
        """Verify database connection is established."""
        assert db_connection is not None, "Database connection is None"

    @pytest.mark.smoke
    def test_can_fetch_data(self, patient_treatment_data):
        """Verify data can be fetched from database."""
        assert patient_treatment_data is not None
        assert len(patient_treatment_data) > 0, "No data retrieved from database"


class TestDataStructure:
    """Tests for basic data structure validation."""

    @pytest.mark.smoke
    def test_patient_treatment_table_exists(self, patient_treatment_data):
        """Verify patient_treatment table has data."""
        assert len(patient_treatment_data) > 0, "patient_treatment table is empty"

    @pytest.mark.smoke
    def test_patient_treatment_has_required_columns(self, patient_treatment_data):
        """Verify patient_treatment table has required columns."""
        required_columns = ['patient_id', 'treatment_cost', 'facility_type', 'visit_date', 'time_spent']
        missing = [col for col in required_columns if col not in patient_treatment_data.columns]
        assert not missing, f"Missing columns: {missing}"

    @pytest.mark.smoke
    def test_data_types_are_reasonable(self, patient_treatment_data):
        """Verify data types are reasonable (not all objects)."""
        numeric_columns = ['patient_id', 'treatment_cost', 'time_spent']
        for col in numeric_columns:
            if col in patient_treatment_data.columns:
                assert patient_treatment_data[col].dtype in ['int64', 'float64', 'int32', 'float32'], \
                    f"Column {col} has unexpected type: {patient_treatment_data[col].dtype}"

    @pytest.mark.smoke
    def test_primary_key_uniqueness(self, db_connection):
        """Verify primary key (id) is unique."""
        query = """
        SELECT COUNT(*) as total_rows,
               COUNT(DISTINCT id) as unique_ids
        FROM patient_treatment
        """
        result = db_connection.get_data_sql(query)
        total = result['total_rows'].iloc[0]
        unique = result['unique_ids'].iloc[0]
        assert total == unique, f"Primary key violation: {total} rows but {unique} unique IDs"


class TestDataRanges:
    """Tests for reasonable data value ranges."""

    @pytest.mark.smoke
    def test_treatment_cost_reasonable(self, patient_treatment_data):
        """Verify treatment costs are within reasonable range."""
        costs = patient_treatment_data['treatment_cost']
        assert (costs >= 0).all(), "Found negative treatment costs"
        assert (costs <= 100000).all(), "Found unreasonably high treatment costs"

    @pytest.mark.smoke
    def test_time_spent_reasonable(self, patient_treatment_data):
        """Verify time spent values are within reasonable range (0-1440 minutes = 24 hours)."""
        times = patient_treatment_data['time_spent']
        assert (times >= 0).all(), "Found negative time spent values"
        assert (times <= 1440).all(), "Found time spent > 24 hours"

    @pytest.mark.smoke
    def test_patient_id_positive(self, patient_treatment_data):
        """Verify patient IDs are positive."""
        patient_ids = patient_treatment_data['patient_id']
        assert (patient_ids > 0).all(), "Found non-positive patient IDs"


class TestFixtures:
    """Tests to verify test fixtures are working."""

    @pytest.mark.smoke
    def test_parquet_reader_fixture_available(self, parquet_reader):
        """Verify ParquetReader fixture is available."""
        assert parquet_reader is not None, "parquet_reader fixture is None"

    @pytest.mark.smoke
    def test_data_quality_library_fixture_available(self, data_quality_library):
        """Verify DataQualityLibrary fixture is available."""
        assert data_quality_library is not None, "data_quality_library fixture is None"
        assert hasattr(data_quality_library, 'check_dataset_is_not_empty'), \
            "DataQualityLibrary missing check_dataset_is_not_empty method"
        assert hasattr(data_quality_library, 'check_count'), \
            "DataQualityLibrary missing check_count method"
