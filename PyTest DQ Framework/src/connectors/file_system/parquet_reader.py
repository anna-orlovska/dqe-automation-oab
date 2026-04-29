import pandas as pd
from pathlib import Path


class ParquetReader:
    """Reader for Parquet files."""

    @staticmethod
    def process(file_path: str, include_subfolders: bool = False) -> pd.DataFrame:
        """
        Read Parquet file(s) into a pandas DataFrame.

        If file_path points to a directory, reads all parquet files in that directory.
        If include_subfolders is True, recursively reads parquet files from subdirectories.

        Args:
            file_path: Path to Parquet file or directory containing Parquet files
            include_subfolders: Whether to recursively search subdirectories (default: False)

        Returns:
            pandas DataFrame with combined data from all parquet files

        Raises:
            FileNotFoundError: If the specified path does not exist
            ValueError: If no parquet files are found
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {file_path}")

        parquet_files = []

        if path.is_file():
            if path.suffix.lower() == ".parquet":
                parquet_files.append(path)
            else:
                raise ValueError(f"File is not a Parquet file: {file_path}")
        elif path.is_dir():
            if include_subfolders:
                parquet_files = list(path.rglob("*.parquet"))
            else:
                parquet_files = list(path.glob("*.parquet"))

        if not parquet_files:
            raise ValueError(f"No Parquet files found in: {file_path}")

        dfs = [pd.read_parquet(file) for file in parquet_files]
        return pd.concat(dfs, ignore_index=True)
