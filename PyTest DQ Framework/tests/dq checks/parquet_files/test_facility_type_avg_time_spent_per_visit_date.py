"""
Description: Data Quality checks for facility_type_avg_time_spent_per_visit_date dataset.
Validates that average time spent per facility type and visit date is correctly calculated.
Requirement(s): FRAMEWORK-012
Author(s): QA Team
"""

import pytest
import os


@pytest.fixture(scope='module')
def source_data(db_connection):
    """Fetch facility type and average time spent data from PostgreSQL."""
    source_query = """
    SELECT
        facility_type,
        visit_date,
        AVG(time_spent) as avg_time_spent,
        COUNT(*) as visit_count
    FROM patient_treatment
    WHERE facility_type IS NOT NULL
        AND visit_date IS NOT NULL
        AND time_spent IS NOT NULL
    GROUP BY facility_type, visit_date
    ORDER BY facility_type, visit_date
    """
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader, parquet_path):
    """Load target data from Parquet files."""
    target_path = os.path.join(parquet_path, 'facility_type_avg_time_spent_per_visit_date')
    return parquet_reader.process(target_path, include_subfolders=True)


class TestSmoke:
    """Smoke tests for facility_type_avg_time_spent dataset."""

    @pytest.mark.smoke
    @pytest.mark.parquet_data
    def test_source_not_empty(self, source_data, data_quality_library):
        """Verify source dataset is not empty."""
        data_quality_library.check_dataset_is_not_empty(source_data)

    @pytest.mark.smoke
    @pytest.mark.parquet_data
    def test_target_not_empty(self, target_data, data_quality_library):
        """Verify target dataset is not empty."""
        data_quality_library.check_dataset_is_not_empty(target_data)

    @pytest.mark.smoke
    @pytest.mark.parquet_data
    def test_source_columns_exist(self, source_data):
        """Verify source has required columns."""
        required_columns = ['facility_type', 'visit_date', 'avg_time_spent']
        missing = [col for col in required_columns if col not in source_data.columns]
        assert not missing, f"Missing columns in source: {missing}"

    @pytest.mark.smoke
    @pytest.mark.parquet_data
    def test_target_columns_exist(self, target_data):
        """Verify target has required columns."""
        required_columns = ['facility_type', 'visit_date', 'avg_time_spent']
        missing = [col for col in required_columns if col not in target_data.columns]
        assert not missing, f"Missing columns in target: {missing}"


class TestCompleteness:
    """Completeness tests for facility_type_avg_time_spent dataset."""

    @pytest.mark.completeness
    @pytest.mark.parquet_data
    def test_source_no_nulls_key_columns(self, source_data, data_quality_library):
        """Verify source has no nulls in key columns."""
        key_columns = ['facility_type', 'visit_date', 'avg_time_spent']
        data_quality_library.check_data_completeness(source_data, key_columns)

    @pytest.mark.completeness
    @pytest.mark.parquet_data
    def test_target_no_nulls_key_columns(self, target_data, data_quality_library):
        """Verify target has no nulls in key columns."""
        key_columns = ['facility_type', 'visit_date', 'avg_time_spent']
        data_quality_library.check_data_completeness(target_data, key_columns)

    @pytest.mark.completeness
    @pytest.mark.parquet_data
    def test_source_no_nulls_all_columns(self, source_data, data_quality_library):
        """Verify source has no nulls in all columns."""
        data_quality_library.check_data_completeness(source_data)

    @pytest.mark.completeness
    @pytest.mark.parquet_data
    def test_target_no_nulls_all_columns(self, target_data, data_quality_library):
        """Verify target has no nulls in all columns."""
        data_quality_library.check_data_completeness(target_data)


class TestQuality:
    """Data quality tests for facility_type_avg_time_spent dataset."""

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_source_no_duplicates(self, source_data, data_quality_library):
        """Verify source has no duplicate facility_type/visit_date combinations."""
        data_quality_library.check_duplicates(source_data, column_names=['facility_type', 'visit_date'])

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_target_no_duplicates(self, target_data, data_quality_library):
        """Verify target has no duplicate facility_type/visit_date combinations."""
        data_quality_library.check_duplicates(target_data, column_names=['facility_type', 'visit_date'])

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_source_avg_time_spent_positive(self, source_data):
        """Verify avg_time_spent values are positive."""
        negative = (source_data['avg_time_spent'] < 0).sum()
        assert negative == 0, f"Found {negative} negative avg_time_spent values in source"

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_target_avg_time_spent_positive(self, target_data):
        """Verify avg_time_spent values are positive."""
        negative = (target_data['avg_time_spent'] < 0).sum()
        assert negative == 0, f"Found {negative} negative avg_time_spent values in target"

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_facility_type_valid_values(self, source_data):
        """Verify facility_type contains expected values."""
        valid_types = {'Hospital', 'Clinic', 'Laboratory'}
        invalid = source_data[~source_data['facility_type'].isin(valid_types)]
        assert len(invalid) == 0, f"Found invalid facility types: {invalid['facility_type'].unique().tolist()}"

    @pytest.mark.quality
    @pytest.mark.parquet_data
    def test_source_target_row_count_match(self, source_data, target_data, data_quality_library):
        """Verify source and target have matching row counts."""
        data_quality_library.check_count(source_data, target_data)
