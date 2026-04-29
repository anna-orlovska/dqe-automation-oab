"""
Description: Example tests demonstrating the PyTest DQ Framework
Requirement(s): FRAMEWORK-001
Author(s): QA Team
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    """Fetch source data from PostgreSQL database."""
    source_query = """
    SELECT
        patient_id,
        treatment_cost,
        facility_type,
        visit_date,
        time_spent
    FROM patient_treatment
    LIMIT 1000
    """
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    """Load target data from Parquet file."""
    target_path = 'parquet_data/patient_sum_treatment_cost_per_facility_type'
    return parquet_reader.process(target_path, include_subfolders=False)


class TestSmoke:
    """Smoke tests - quick sanity checks on data structure."""

    @pytest.mark.smoke
    @pytest.mark.example
    def test_source_dataset_is_not_empty(self, source_data, data_quality_library):
        """Verify source dataset is not empty."""
        data_quality_library.check_dataset_is_not_empty(source_data)

    @pytest.mark.smoke
    @pytest.mark.example
    def test_target_dataset_is_not_empty(self, target_data, data_quality_library):
        """Verify target dataset is not empty."""
        data_quality_library.check_dataset_is_not_empty(target_data)

    @pytest.mark.smoke
    @pytest.mark.example
    def test_source_has_required_columns(self, source_data):
        """Verify source data has required columns."""
        required_columns = ['patient_id', 'treatment_cost', 'facility_type']
        missing_columns = [col for col in required_columns if col not in source_data.columns]
        assert not missing_columns, f"Missing required columns: {missing_columns}"

    @pytest.mark.smoke
    @pytest.mark.example
    def test_target_has_required_columns(self, target_data):
        """Verify target data has required columns."""
        required_columns = ['patient_id', 'facility_type', 'total_cost']
        missing_columns = [col for col in required_columns if col not in target_data.columns]
        assert not missing_columns, f"Missing required columns: {missing_columns}"


class TestCompleteness:
    """Completeness tests - verify data has no missing values."""

    @pytest.mark.completeness
    @pytest.mark.example
    def test_source_no_nulls_in_key_columns(self, source_data, data_quality_library):
        """Verify source data has no null values in key columns."""
        key_columns = ['patient_id', 'treatment_cost']
        data_quality_library.check_data_completeness(source_data, key_columns)

    @pytest.mark.completeness
    @pytest.mark.example
    def test_target_no_nulls_in_key_columns(self, target_data, data_quality_library):
        """Verify target data has no null values in key columns."""
        key_columns = ['patient_id', 'total_cost']
        data_quality_library.check_data_completeness(target_data, key_columns)

    @pytest.mark.completeness
    @pytest.mark.example
    def test_source_no_nulls_all_columns(self, source_data, data_quality_library):
        """Verify source data has no null values in any column."""
        data_quality_library.check_data_completeness(source_data)

    @pytest.mark.completeness
    @pytest.mark.example
    def test_target_no_nulls_all_columns(self, target_data, data_quality_library):
        """Verify target data has no null values in any column."""
        data_quality_library.check_data_completeness(target_data)


class TestQuality:
    """Data quality tests - advanced DQ checks."""

    @pytest.mark.quality
    @pytest.mark.example
    def test_source_no_duplicates(self, source_data, data_quality_library):
        """Verify source data has no duplicate rows (by patient_id)."""
        data_quality_library.check_duplicates(source_data, column_names=['patient_id', 'visit_date'])

    @pytest.mark.quality
    @pytest.mark.example
    def test_target_no_duplicates(self, target_data, data_quality_library):
        """Verify target data has no duplicate rows."""
        data_quality_library.check_duplicates(target_data, column_names=['patient_id', 'facility_type'])

    @pytest.mark.quality
    @pytest.mark.example
    def test_source_treatment_cost_positive(self, source_data):
        """Verify all treatment costs are positive values."""
        negative_costs = (source_data['treatment_cost'] < 0).sum()
        assert negative_costs == 0, f"Found {negative_costs} rows with negative treatment costs"

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_target_treatment_cost_positive(self, target_data):
        """Verify all treatment costs in target are positive values."""
        negative_costs = (target_data['total_cost'] < 0).sum()
        assert negative_costs == 0, f"Found {negative_costs} rows with negative total costs"
