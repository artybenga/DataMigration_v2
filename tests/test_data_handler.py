import pytest
import pandas as pd
import numpy as np


def test_load_csv_file(data_handler, sample_csv_path):
    """Test loading a CSV file"""
    dataframes = data_handler.load_file(str(sample_csv_path))

    assert len(dataframes) == 1
    df = list(dataframes.values())[0]

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert len(df.columns) == 3
    assert df.isna().sum().sum() == 3  # Check NULL handling


def test_load_excel_file(data_handler, sample_excel_path):
    """Test loading an Excel file with multiple sheets"""
    dataframes = data_handler.load_file(str(sample_excel_path))

    assert len(dataframes) == 2  # Two sheets
    assert all(isinstance(df, pd.DataFrame) for df in dataframes.values())

    # Check sheet names
    assert any('Sheet1' in key for key in dataframes.keys())
    assert any('Sheet2' in key for key in dataframes.keys())


def test_load_nonexistent_file(data_handler):
    """Test loading a non-existent file"""
    with pytest.raises(Exception):
        data_handler.load_file("nonexistent.csv")


def test_null_handling(data_handler, sample_csv_path):
    """Test proper handling of NULL values"""
    dataframes = data_handler.load_file(str(sample_csv_path))
    df = list(dataframes.values())[0]

    # Check if NaN values are properly handled
    assert pd.isna(df['Column One'].iloc[2])
    assert pd.isna(df['Column Two'].iloc[1])
    assert pd.isna(df['Column-Three'].iloc[2])