"""
Description: Advanced data quality checks for comprehensive validation.
Tests duplicates, nulls, consistency, and data integrity across datasets.
Requirement(s): FRAMEWORK-014
Author(s): QA Team
"""

import pytest
import pandas as pd
import os


@pytest.fixture(scope='module')
def source_treatment_data(db_connection):
    """Fetch all patient treatment data from source."""
    query = """
    SELECT
        patient_id,
        treatment_cost,
        facility_type,
        visit_date,
        time_spent
    FROM patient_treatment
    ORDER BY patient_id, visit_date
    """
    return db_connection.get_data_sql(query)


@pytest.fixture(scope='module')
def aggregated_source(db_connection):
    """Fetch aggregated patient treatment cost by facility type."""
    query = """
    SELECT
        patient_id,
        facility_type,
        SUM(treatment_cost) as total_cost,
        COUNT(*) as visit_count
    FROM patient_treatment
    GROUP BY patient_id, facility_type
    ORDER BY patient_id, facility_type
    """
    return db_connection.get_data_sql(query)


@pytest.fixture(scope='module')
def target_aggregated(parquet_reader, parquet_path):
    """Load aggregated target data from Parquet."""
    target_path = os.path.join(parquet_path, 'patient_sum_treatment_cost_per_facility_type')
    return parquet_reader.process(target_path, include_subfolders=True)


class TestDuplicateDetection:
    """Tests for detecting duplicate records."""

    @pytest.mark.quality
    def test_source_no_row_duplicates(self, source_treatment_data, data_quality_library):
        """Verify source has no exact duplicate rows."""
        data_quality_library.check_duplicates(source_treatment_data)

    @pytest.mark.quality
    def test_source_no_patient_visit_duplicates(self, source_treatment_data, data_quality_library):
        """Verify source has no duplicate patient visits on same date."""
        data_quality_library.check_duplicates(
            source_treatment_data,
            column_names=['patient_id', 'visit_date']
        )

    @pytest.mark.quality
    def test_aggregated_no_duplicates(self, aggregated_source, data_quality_library):
        """Verify aggregated source has no duplicate patient/facility combinations."""
        data_quality_library.check_duplicates(
            aggregated_source,
            column_names=['patient_id', 'facility_type']
        )

    @pytest.mark.quality
    def test_target_no_duplicates(self, target_aggregated, data_quality_library):
        """Verify target has no duplicate patient/facility combinations."""
        data_quality_library.check_duplicates(
            target_aggregated,
            column_names=['patient_id', 'facility_type']
        )


class TestNullValues:
    """Tests for null value detection and validation."""

    @pytest.mark.quality
    def test_source_no_nulls(self, source_treatment_data, data_quality_library):
        """Verify source has no null values in any column."""
        data_quality_library.check_data_completeness(source_treatment_data)

    @pytest.mark.quality
    def test_aggregated_source_no_nulls(self, aggregated_source, data_quality_library):
        """Verify aggregated source has no null values."""
        data_quality_library.check_data_completeness(aggregated_source)

    @pytest.mark.quality
    def test_target_no_nulls(self, target_aggregated, data_quality_library):
        """Verify target has no null values."""
        data_quality_library.check_data_completeness(target_aggregated)

    @pytest.mark.quality
    def test_numeric_columns_no_nulls(self, source_treatment_data, data_quality_library):
        """Verify numeric columns have no null values."""
        numeric_cols = ['patient_id', 'treatment_cost', 'time_spent']
        data_quality_library.check_data_completeness(source_treatment_data, numeric_cols)


class TestDataConsistency:
    """Tests for consistency between source and target datasets."""

    @pytest.mark.quality
    def test_aggregated_row_count(self, aggregated_source, target_aggregated, data_quality_library):
        """Verify source and target aggregated data have same row count."""
        data_quality_library.check_count(aggregated_source, target_aggregated)

    @pytest.mark.quality
    def test_patient_ids_match(self, aggregated_source, target_aggregated, data_quality_library):
        """Verify both datasets have same patient IDs."""
        source_patients = set(aggregated_source['patient_id'].unique())
        target_patients = set(target_aggregated['patient_id'].unique())
        missing_in_target = source_patients - target_patients
        missing_in_source = target_patients - source_patients
        assert not missing_in_target, f"Patient IDs missing in target: {missing_in_target}"
        assert not missing_in_source, f"Patient IDs in target but not source: {missing_in_source}"

    @pytest.mark.quality
    def test_facility_types_match(self, aggregated_source, target_aggregated):
        """Verify both datasets have same facility types."""
        source_types = set(aggregated_source['facility_type'].unique())
        target_types = set(target_aggregated['facility_type'].unique())
        assert source_types == target_types, \
            f"Facility types mismatch. Source: {source_types}, Target: {target_types}"

    @pytest.mark.quality
    def test_total_cost_values_match(self, aggregated_source, target_aggregated):
        """Verify total cost values match between source and target."""
        merged = aggregated_source.merge(
            target_aggregated,
            on=['patient_id', 'facility_type'],
            how='inner'
        )
        cost_differences = (merged['total_cost_x'] - merged['total_cost_y']).abs()
        assert (cost_differences < 0.01).all(), \
            f"Cost differences found: {cost_differences[cost_differences >= 0.01].tolist()}"


class TestDataValidation:
    """Tests for data validation and business rules."""

    @pytest.mark.quality
    def test_treatment_cost_not_negative(self, source_treatment_data):
        """Verify all treatment costs are non-negative."""
        negative_costs = source_treatment_data[source_treatment_data['treatment_cost'] < 0]
        assert len(negative_costs) == 0, f"Found {len(negative_costs)} negative treatment costs"

    @pytest.mark.quality
    def test_time_spent_not_negative(self, source_treatment_data):
        """Verify all time spent values are non-negative."""
        negative_times = source_treatment_data[source_treatment_data['time_spent'] < 0]
        assert len(negative_times) == 0, f"Found {len(negative_times)} negative time spent values"

    @pytest.mark.quality
    def test_visit_count_positive(self, aggregated_source):
        """Verify visit count is always positive."""
        invalid_counts = aggregated_source[aggregated_source['visit_count'] <= 0]
        assert len(invalid_counts) == 0, f"Found {len(invalid_counts)} invalid visit counts"

    @pytest.mark.quality
    def test_facility_type_not_empty(self, source_treatment_data):
        """Verify facility type is never empty string."""
        empty_facility = source_treatment_data[
            (source_treatment_data['facility_type'] == '') |
            (source_treatment_data['facility_type'].isna())
        ]
        assert len(empty_facility) == 0, f"Found {len(empty_facility)} empty facility types"

    @pytest.mark.quality
    def test_valid_visit_dates(self, source_treatment_data):
        """Verify visit dates are in valid format and reasonable range."""
        try:
            dates = pd.to_datetime(source_treatment_data['visit_date'])
            future_dates = dates[dates > pd.Timestamp.now()]
            assert len(future_dates) == 0, f"Found {len(future_dates)} future dates"
        except Exception as e:
            pytest.fail(f"Invalid date format: {str(e)}")


class TestDataMofidence:
    """Tests for data quality confidence metrics."""

    @pytest.mark.quality
    def test_dataset_size_reasonable(self, source_treatment_data):
        """Verify dataset has reasonable size for testing."""
        min_rows = 5
        assert len(source_treatment_data) >= min_rows, \
            f"Dataset too small: {len(source_treatment_data)} rows (minimum: {min_rows})"

    @pytest.mark.quality
    def test_facility_type_distribution(self, source_treatment_data):
        """Verify we have data from multiple facility types."""
        facility_types = source_treatment_data['facility_type'].unique()
        assert len(facility_types) >= 2, \
            f"Need at least 2 facility types, found {len(facility_types)}: {facility_types}"

    @pytest.mark.quality
    def test_multiple_patients(self, source_treatment_data):
        """Verify data includes multiple patients."""
        patient_count = source_treatment_data['patient_id'].nunique()
        min_patients = 3
        assert patient_count >= min_patients, \
            f"Need at least {min_patients} patients, found {patient_count}"

    @pytest.mark.quality
    def test_aggregation_correctness(self, source_treatment_data, aggregated_source):
        """Verify aggregation calculations are correct."""
        for _, agg_row in aggregated_source.iterrows():
            patient_id = agg_row['patient_id']
            facility_type = agg_row['facility_type']

            source_subset = source_treatment_data[
                (source_treatment_data['patient_id'] == patient_id) &
                (source_treatment_data['facility_type'] == facility_type)
            ]

            expected_cost = source_subset['treatment_cost'].sum()
            expected_count = len(source_subset)

            assert abs(agg_row['total_cost'] - expected_cost) < 0.01, \
                f"Cost mismatch for patient {patient_id}, facility {facility_type}"
            assert agg_row['visit_count'] == expected_count, \
                f"Visit count mismatch for patient {patient_id}, facility {facility_type}"
