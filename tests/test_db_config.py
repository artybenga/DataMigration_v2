import pytest
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError


def test_db_connection(mock_db_config):
    """Test database connection"""
    assert mock_db_config.connect()


def test_table_creation(mock_db_config):
    """Test table creation from DataFrame"""
    df = pd.DataFrame({
        'Column One': [1, 2, 3],
        'Column Two': ['a', 'b', 'c']
    })

    assert mock_db_config.create_table_from_df(df, 'test_table')


def test_column_name_cleaning(mock_db_config):
    """Test cleaning of column names"""
    df = pd.DataFrame({
        'Column One': [1],
        'Column-Two': [2],
        'Column Three': [3]
    })

    mock_db_config.create_table_from_df(df, 'test_table')

    # Check if column names were cleaned
    cleaned_columns = list(df.columns)
    assert all('_' in col for col in cleaned_columns)
    assert ' ' not in ''.join(cleaned_columns)
    assert '-' not in ''.join(cleaned_columns)


def test_connection_error(mocker):
    """Test handling of database connection error"""
    # Mock SQLAlchemy create_engine to raise an error
    mocker.patch('sqlalchemy.create_engine', side_effect=SQLAlchemyError)

    db_config = mocker.Mock()
    assert not db_config.connect()