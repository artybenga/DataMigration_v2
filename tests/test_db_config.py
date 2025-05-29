import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import os
import pandas as pd
import numpy as np
from sqlalchemy.exc import SQLAlchemyError
from utils.db_config import DatabaseConfig


class TestDatabaseConfigGetConnectionString(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = Mock(spec=logging.Logger)

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'testdb'
    })
    def test_get_connection_string_all_env_vars_present(self, mock_load_dotenv):
        """Test connection string generation with all environment variables present."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://testuser:testpass@localhost:5432/testdb"

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)
        mock_load_dotenv.assert_called_once()

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': 'user@example.com',
        'DB_PASSWORD': 'p@ssw0rd!',
        'DB_HOST': 'db.example.com',
        'DB_PORT': '3306',
        'DB_NAME': 'production_db'
    })
    def test_get_connection_string_special_characters(self, mock_load_dotenv):
        """Test connection string with special characters in credentials."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://user@example.com:p@ssw0rd!@db.example.com:3306/production_db"

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_connection_string_missing_env_vars(self, mock_load_dotenv):
        """Test connection string generation when environment variables are missing."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://None:None@None:None/None"

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': '',
        'DB_PASSWORD': '',
        'DB_HOST': '',
        'DB_PORT': '',
        'DB_NAME': ''
    })
    def test_get_connection_string_empty_env_vars(self, mock_load_dotenv):
        """Test connection string generation with empty environment variables."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://:@:/"

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'None'
    })
    def test_get_connection_string_partial_env_vars(self, mock_load_dotenv):
        """Test connection string generation with some missing environment variables."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://testuser:testpass@localhost:5432/None"

        # Remove the DB_NAME var
        del os.environ['DB_NAME']

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': 'user with spaces',
        'DB_PASSWORD': 'pass with spaces',
        'DB_HOST': 'host-with-dashes',
        'DB_PORT': '5432',
        'DB_NAME': 'db_with_underscores'
    })
    def test_get_connection_string_with_spaces_and_special_chars(self, mock_load_dotenv):
        """Test connection string with spaces and various special characters."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)
        expected_conn_string = "postgresql://user with spaces:pass with spaces@host-with-dashes:5432/db_with_underscores"

        # Act
        result = db_config.get_connection_string()

        # Assert
        self.assertEqual(result, expected_conn_string)

    @patch('utils.db_config.load_dotenv')
    def test_get_connection_string_calls_load_dotenv(self, mock_load_dotenv):
        """Test that get_connection_string method calls load_dotenv during initialization."""
        # Act
        db_config = DatabaseConfig(self.mock_logger)

        # Assert
        mock_load_dotenv.assert_called_once()

    @patch('utils.db_config.load_dotenv')
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'testdb'
    })
    def test_get_connection_string_multiple_calls_same_result(self, mock_load_dotenv):
        """Test that multiple calls to get_connection_string return the same result."""
        # Arrange
        db_config = DatabaseConfig(self.mock_logger)

        # Act
        result1 = db_config.get_connection_string()
        result2 = db_config.get_connection_string()

        # Assert
        self.assertEqual(result1, result2)
        self.assertEqual(result1, "postgresql://testuser:testpass@localhost:5432/testdb")


class TestDatabaseConfig(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.db_config = DatabaseConfig(self.mock_logger)

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_success(self, mock_load_dotenv, mock_create_engine):
        """Test successful database connection."""
        # Arrange
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        # Act
        result = self.db_config.connect()

        # Assert
        self.assertTrue(result)
        self.assertEqual(self.db_config.engine, mock_engine)
        mock_create_engine.assert_called_once()
        self.mock_logger.info.assert_called_once_with("Successfully connected to database")
        self.mock_logger.error.assert_not_called()

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_failure_sqlalchemy_error(self, mock_load_dotenv, mock_create_engine):
        """Test connection failure with SQLAlchemy error."""
        # Arrange
        error_message = "Connection timeout"
        mock_create_engine.side_effect = SQLAlchemyError(error_message)

        # Act
        result = self.db_config.connect()

        # Assert
        self.assertFalse(result)
        self.assertIsNone(self.db_config.engine)
        mock_create_engine.assert_called_once()
        self.mock_logger.error.assert_called_once_with(f"Database connection error: {error_message}")
        self.mock_logger.info.assert_not_called()

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_failure_generic_exception(self, mock_load_dotenv, mock_create_engine):
        """Test connection failure with generic exception."""
        # Arrange
        error_message = "Network unreachable"
        mock_create_engine.side_effect = Exception(error_message)

        # Act
        result = self.db_config.connect()

        # Assert
        self.assertFalse(result)
        self.assertIsNone(self.db_config.engine)
        mock_create_engine.assert_called_once()
        self.mock_logger.error.assert_called_once_with(f"Database connection error: {error_message}")
        self.mock_logger.info.assert_not_called()

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_calls_get_connection_string(self, mock_load_dotenv, mock_create_engine):
        """Test that connect method uses get_connection_string method."""
        # Arrange
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        with patch.object(self.db_config, 'get_connection_string') as mock_get_conn_str:
            mock_get_conn_str.return_value = "postgresql://user:pass@host:5432/db"

            # Act
            result = self.db_config.connect()

            # Assert
            self.assertTrue(result)
            mock_get_conn_str.assert_called_once()
            mock_create_engine.assert_called_once_with("postgresql://user:pass@host:5432/db")

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_multiple_calls(self, mock_load_dotenv, mock_create_engine):
        """Test multiple calls to connect method."""
        # Arrange
        mock_engine1 = Mock()
        mock_engine2 = Mock()
        mock_create_engine.side_effect = [mock_engine1, mock_engine2]

        # Act
        result1 = self.db_config.connect()
        result2 = self.db_config.connect()

        # Assert
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertEqual(self.db_config.engine, mock_engine2)  # Should be the latest engine
        self.assertEqual(mock_create_engine.call_count, 2)
        self.assertEqual(self.mock_logger.info.call_count, 2)

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_empty_exception_message(self, mock_load_dotenv, mock_create_engine):
        """Test connection failure with empty exception message."""
        # Arrange
        mock_create_engine.side_effect = Exception("")

        # Act
        result = self.db_config.connect()

        # Assert
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once_with("Database connection error: ")

    @patch('utils.db_config.create_engine')
    @patch('utils.db_config.load_dotenv')
    def test_connect_exception_with_special_characters(self, mock_load_dotenv, mock_create_engine):
        """Test connection failure with special characters in error message."""
        # Arrange
        error_message = "Connection failed: 'invalid credentials' & timeout"
        mock_create_engine.side_effect = Exception(error_message)

        # Act
        result = self.db_config.connect()

        # Assert
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once_with(f"Database connection error: {error_message}")


class TestDatabaseConfigCreateTableFromDf(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_engine = Mock()
        self.db_config = DatabaseConfig(self.mock_logger)
        self.db_config.engine = self.mock_engine

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_success(self, mock_to_sql, mock_load_dotenv):
        """Test successful table creation from DataFrame."""
        # Arrange
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [25, 30],
            'city': ['New York', 'London']
        })
        table_name = 'test_table'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        mock_to_sql.assert_called_once_with(table_name, self.mock_engine, if_exists='replace', index=False)
        self.mock_logger.info.assert_called_once_with(f"Successfully created table: {table_name}")
        self.mock_logger.error.assert_not_called()

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_column_name_cleaning(self, mock_to_sql, mock_load_dotenv):
        """Test that column names with spaces and hyphens are cleaned."""
        # Arrange
        df = pd.DataFrame({
            'first name': ['Alice'],
            'last-name': ['Smith'],
            'age group': [25],
            'home-address': ['123 Main St']
        })
        table_name = 'test_table'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        # Check that column names were cleaned
        expected_columns = ['first_name', 'last_name', 'age_group', 'home_address']
        self.assertEqual(list(df.columns), expected_columns)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_to_sql_exception(self, mock_to_sql, mock_load_dotenv):
        """Test handling of exceptions during to_sql operation."""
        # Arrange
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        table_name = 'test_table'
        error_message = "Table creation failed"
        mock_to_sql.side_effect = Exception(error_message)

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once_with(f"Error creating table {table_name}: {error_message}")
        self.mock_logger.info.assert_not_called()

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_sqlalchemy_exception(self, mock_to_sql, mock_load_dotenv):
        """Test handling of SQLAlchemy-specific exceptions."""
        # Arrange
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        table_name = 'test_table'
        error_message = "Connection lost"
        mock_to_sql.side_effect = SQLAlchemyError(error_message)

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once_with(f"Error creating table {table_name}: {error_message}")

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_empty_dataframe(self, mock_to_sql, mock_load_dotenv):
        """Test table creation with empty DataFrame."""
        # Arrange
        df = pd.DataFrame()
        table_name = 'empty_table'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        mock_to_sql.assert_called_once_with(table_name, self.mock_engine, if_exists='replace', index=False)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_single_row(self, mock_to_sql, mock_load_dotenv):
        """Test table creation with single row DataFrame."""
        # Arrange
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        table_name = 'single_row_table'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        mock_to_sql.assert_called_once_with(table_name, self.mock_engine, if_exists='replace', index=False)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_special_table_name(self, mock_to_sql, mock_load_dotenv):
        """Test table creation with special characters in table name."""
        # Arrange
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        table_name = 'test_table_123'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        mock_to_sql.assert_called_once_with(table_name, self.mock_engine, if_exists='replace', index=False)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_mixed_data_types(self, mock_to_sql, mock_load_dotenv):
        """Test table creation with mixed data types."""
        # Arrange
        df = pd.DataFrame({
            'string_col': ['Alice', 'Bob'],
            'int_col': [25, 30],
            'float_col': [1.5, 2.7],
            'bool_col': [True, False],
            'date_col': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-02-01')]
        })
        table_name = 'mixed_types_table'
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)
        mock_to_sql.assert_called_once_with(table_name, self.mock_engine, if_exists='replace', index=False)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    def test_create_table_from_df_no_engine(self, mock_to_sql, mock_load_dotenv):
        """Test table creation when engine is None."""
        # Arrange
        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        table_name = 'test_table'
        self.db_config.engine = None
        mock_to_sql.side_effect = AttributeError("'NoneType' object has no attribute 'execute'")

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertFalse(result)
        self.mock_logger.error.assert_called_once()

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    @patch('pandas.DataFrame.replace')
    def test_create_table_from_df_handles_nat_nan(self, mock_replace, mock_to_sql, mock_load_dotenv):
        """Test that NaT and NaN values trigger replacement methods."""
        # Arrange
        df = pd.DataFrame({
            'name': ['Alice', np.nan, 'Charlie'],
            'date': [pd.Timestamp('2023-01-01'), pd.NaT, pd.Timestamp('2023-03-01')],
            'value': [1.5, np.nan, 3.0]
        })
        table_name = 'test_table'

        # Mock the return values to simulate the chain of operations
        mock_replace.return_value = df  # replace() returns a DataFrame
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)

        # Verify that replace was called with NaT -> None
        mock_replace.assert_called_once_with({pd.NaT: None, np.nan: None})

        # Verify to_sql was called
        mock_to_sql.assert_called_once_with(table_name, self.db_config.engine, if_exists='replace', index=False)

    @patch('utils.db_config.load_dotenv')
    @patch('pandas.DataFrame.to_sql')
    @patch('pandas.DataFrame.replace')
    def test_create_table_from_df_no_nan_values(self, mock_replace, mock_to_sql, mock_load_dotenv):
        """Test behavior when no NaT/NaN values are present."""
        # Arrange - DataFrame with no NaN or NaT values
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'date': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-02-01'), pd.Timestamp('2023-03-01')],
            'value': [1.5, 2.5, 3.0]
        })
        table_name = 'test_table'

        # Mock the return values
        mock_replace.return_value = df
        mock_to_sql.return_value = None

        # Act
        result = self.db_config.create_table_from_df(df, table_name)

        # Assert
        self.assertTrue(result)

        # Even with no NaN values, replace and where are still called
        # (the method always calls them regardless of content)
        mock_replace.assert_called_once_with({pd.NaT: None, np.nan: None})
        mock_to_sql.assert_called_once_with(table_name, self.db_config.engine, if_exists='replace', index=False)

