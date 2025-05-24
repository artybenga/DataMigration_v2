import pytest
import pandas as pd
import os
import logging
from pathlib import Path
from utils.logger_config import setup_logger
from utils.db_config import DatabaseConfig
from utils.data_handler import DataHandler


@pytest.fixture
def sample_csv_path(tmp_path):
    """Create a sample CSV file for testing"""
    file_path = tmp_path / "sample.csv"
    df = pd.DataFrame({
        'Column One': [1, 2, None],
        'Column Two': ['a', None, 'c'],
        'Column-Three': [1.1, 2.2, None]
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_excel_path(tmp_path):
    """Create a sample Excel file with multiple sheets for testing"""
    file_path = tmp_path / "sample.xlsx"
    df1 = pd.DataFrame({
        'Sheet One Col': [1, 2, None],
        'Sheet One Col Two': ['a', None, 'c']
    })
    df2 = pd.DataFrame({
        'Sheet Two Col': [4, 5, None],
        'Sheet Two Col Two': ['d', None, 'f']
    })

    with pd.ExcelWriter(file_path) as writer:
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)
    return file_path


@pytest.fixture
def test_logger(tmp_path):
    """Create a test logger"""
    log_file = tmp_path / "test.log"
    return setup_logger(str(log_file))


@pytest.fixture
def mock_db_config(mocker):
    """Mock database configuration"""
    mock_engine = mocker.Mock()
    mock_engine.connect.return_value = mocker.Mock()

    mocker.patch('sqlalchemy.create_engine', return_value=mock_engine)
    return DatabaseConfig(logging.getLogger())


@pytest.fixture
def data_handler(test_logger):
    """Create a DataHandler instance"""
    return DataHandler(test_logger)