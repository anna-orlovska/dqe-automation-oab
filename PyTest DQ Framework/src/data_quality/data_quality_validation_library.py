import pandas as pd


class DataQualityLibrary:
    """Library of static methods for performing data quality checks on pandas DataFrames."""

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame) -> None:
        """
        Verify that dataset is not empty.

        Args:
            df: DataFrame to check

        Raises:
            AssertionError: If dataset is empty
        """
        assert len(df) > 0, f"Dataset is empty. Expected at least 1 row, got {len(df)} rows"

    @staticmethod
    def check_count(df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        """
        Verify that two datasets have the same row count.

        Args:
            df1: First DataFrame (source)
            df2: Second DataFrame (target)

        Raises:
            AssertionError: If row counts do not match
        """
        count1 = len(df1)
        count2 = len(df2)
        assert count1 == count2, f"Row count mismatch. Source: {count1} rows, Target: {count2} rows"

    @staticmethod
    def check_data_completeness(df: pd.DataFrame, column_names: list = None) -> None:
        """
        Verify that specified columns have no null values.

        Args:
            df: DataFrame to check
            column_names: List of column names to check (default: all columns)

        Raises:
            AssertionError: If any specified column contains null values
        """
        cols_to_check = column_names if column_names else df.columns.tolist()

        for col in cols_to_check:
            null_count = df[col].isna().sum()
            assert null_count == 0, (
                f"Column '{col}' contains null values. "
                f"Found {null_count} null values out of {len(df)} rows"
            )

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names: list = None) -> None:
        """
        Verify that dataset contains no duplicate rows.

        Args:
            df: DataFrame to check
            column_names: List of column names to check for duplicates (default: all columns)

        Raises:
            AssertionError: If duplicate rows are found
        """
        if column_names:
            duplicates = df.duplicated(subset=column_names, keep=False).sum()
        else:
            duplicates = df.duplicated(keep=False).sum()

        assert duplicates == 0, (
            f"Found {duplicates} duplicate row(s) in dataset. "
            f"Columns checked: {column_names if column_names else 'all'}"
        )

    @staticmethod
    def check_not_null_values(df: pd.DataFrame, column_names: list = None) -> None:
        """
        Verify that specified columns have no null values (alias for check_data_completeness).

        Args:
            df: DataFrame to check
            column_names: List of column names to check (default: all columns)

        Raises:
            AssertionError: If any specified column contains null values
        """
        DataQualityLibrary.check_data_completeness(df, column_names)

    @staticmethod
    def check_consistency(df1: pd.DataFrame, df2: pd.DataFrame, column_names: list = None) -> None:
        """
        Verify that two datasets have the same column values for specified columns.

        Args:
            df1: First DataFrame (source)
            df2: Second DataFrame (target)
            column_names: List of column names to compare (default: common columns)

        Raises:
            AssertionError: If column values do not match
        """
        if column_names is None:
            column_names = list(set(df1.columns) & set(df2.columns))

        if len(df1) != len(df2):
            raise AssertionError(
                f"Cannot check consistency: row counts differ. "
                f"Source: {len(df1)} rows, Target: {len(df2)} rows"
            )

        for col in column_names:
            if col not in df1.columns or col not in df2.columns:
                raise ValueError(f"Column '{col}' not found in one or both DataFrames")

            mismatches = (df1[col] != df2[col]).sum()
            assert mismatches == 0, (
                f"Column '{col}' has {mismatches} inconsistent value(s) between source and target"
            )
