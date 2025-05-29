import unittest
from unittest.mock import Mock, patch
import pandas as pd
from utils.data_handler import DataHandler


class TestDataHandler(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = Mock()
        self.data_handler = DataHandler(self.mock_logger)

    def tearDown(self):
        """Clean up after each test."""
        self.data_handler.dataframes.clear()

    @patch('pandas.read_csv')
    def test_load_csv_file_success(self, mock_read_csv):
        """Test successful loading of CSV file."""
        # Setup test data
        test_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['NYC', 'LA', 'Chicago']
        })
        mock_read_csv.return_value = test_data

        # Execute with a real CSV file path
        result = self.data_handler.load_file('test_data.csv')

        # Assertions
        mock_read_csv.assert_called_once_with('test_data.csv', na_values=['', 'NA', 'NULL'])
        self.assertIn('test_data', self.data_handler.dataframes)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['test_data'], test_data)
        self.mock_logger.info.assert_called_once_with("Successfully loaded CSV file: test_data")
        self.assertEqual(result, self.data_handler.dataframes)

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_load_excel_file_single_sheet(self, mock_read_excel, mock_excel_file):
        """Test successful loading of Excel file with single sheet."""
        # Setup test data
        test_data = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'price': [10.5, 20.0, 15.75]
        })
        mock_read_excel.return_value = test_data

        # Mock Excel file behavior
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['Sheet1']
        mock_excel_file.return_value = mock_excel_instance

        # Execute
        result = self.data_handler.load_file('products.xlsx')

        # Assertions
        mock_excel_file.assert_called_once_with('products.xlsx')
        mock_read_excel.assert_called_once_with('products.xlsx', sheet_name='Sheet1', na_values=['', 'NA', 'NULL'])
        self.assertIn('Sheet1', self.data_handler.dataframes)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['Sheet1'], test_data)
        self.mock_logger.info.assert_called_once_with("Successfully loaded Excel file: products")

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_load_excel_file_multiple_sheets(self, mock_read_excel, mock_excel_file):
        """Test successful loading of Excel file with multiple sheets."""
        # Setup test data
        sheet1_data = pd.DataFrame({'col1': [1, 2, 3]})
        sheet2_data = pd.DataFrame({'col2': [4, 5, 6]})
        sheet3_data = pd.DataFrame({'col3': [7, 8, 9]})

        mock_read_excel.side_effect = [sheet1_data, sheet2_data, sheet3_data]

        # Mock Excel file behavior
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['Sales', 'Inventory', 'Reports']
        mock_excel_file.return_value = mock_excel_instance

        # Execute
        result = self.data_handler.load_file('business_data.xlsx')

        # Assertions
        mock_excel_file.assert_called_once_with('business_data.xlsx')
        self.assertEqual(mock_read_excel.call_count, 3)

        # Check all sheets were loaded
        self.assertIn('Sales', self.data_handler.dataframes)
        self.assertIn('Inventory', self.data_handler.dataframes)
        self.assertIn('Reports', self.data_handler.dataframes)

        # Verify data integrity
        pd.testing.assert_frame_equal(self.data_handler.dataframes['Sales'], sheet1_data)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['Inventory'], sheet2_data)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['Reports'], sheet3_data)

        self.mock_logger.info.assert_called_once_with("Successfully loaded Excel file: business_data")

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_load_xls_file_success(self, mock_read_excel, mock_excel_file):
        """Test successful loading of XLS file."""
        # Setup test data
        test_data = pd.DataFrame({'old_format': ['data1', 'data2']})
        mock_read_excel.return_value = test_data

        # Mock Excel file behavior
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['OldSheet']
        mock_excel_file.return_value = mock_excel_instance

        # Execute
        result = self.data_handler.load_file('legacy_file.xls')

        # Assertions
        mock_excel_file.assert_called_once_with('legacy_file.xls')
        mock_read_excel.assert_called_once_with('legacy_file.xls', sheet_name='OldSheet', na_values=['', 'NA', 'NULL'])
        self.assertIn('OldSheet', self.data_handler.dataframes)
        self.mock_logger.info.assert_called_once_with("Successfully loaded Excel file: legacy_file")

    def test_unsupported_file_extension(self):
        """Test handling of unsupported file extensions."""
        # Execute
        result = self.data_handler.load_file('unsupported.txt')

        # Assertions - should return current dataframes dict and no logging
        self.assertEqual(result, self.data_handler.dataframes)
        self.mock_logger.info.assert_not_called()
        self.mock_logger.error.assert_not_called()

    @patch('pandas.read_csv')
    def test_csv_file_not_found(self, mock_read_csv):
        """Test exception handling when CSV file is not found."""
        # Setup exception
        mock_read_csv.side_effect = FileNotFoundError("No such file or directory")

        # Execute and assert exception
        with self.assertRaises(FileNotFoundError):
            self.data_handler.load_file('missing.csv')

        # Verify error logging
        self.mock_logger.error.assert_called_once_with("Error loading file missing.csv: No such file or directory")

    @patch('pandas.ExcelFile')
    def test_excel_file_corrupted(self, mock_excel_file):
        """Test exception handling when Excel file is corrupted."""
        # Setup exception
        mock_excel_file.side_effect = Exception("Excel file appears to be corrupted")

        # Execute and assert exception
        with self.assertRaises(Exception):
            self.data_handler.load_file('corrupted.xlsx')

        # Verify error logging
        self.mock_logger.error.assert_called_once_with(
            "Error loading file corrupted.xlsx: Excel file appears to be corrupted")

    @patch('pandas.read_csv')
    def test_csv_with_na_values(self, mock_read_csv):
        """Test that CSV files are loaded with correct NA values parameter."""
        # Setup test data with NA values
        test_data = pd.DataFrame({
            'name': ['Alice', None, 'Charlie'],
            'value': [1, 2, None]
        })
        mock_read_csv.return_value = test_data

        # Execute
        self.data_handler.load_file('data_with_na.csv')

        # Verify NA values parameter is passed
        mock_read_csv.assert_called_once_with('data_with_na.csv', na_values=['', 'NA', 'NULL'])

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_excel_with_na_values(self, mock_read_excel, mock_excel_file):
        """Test that Excel files are loaded with correct NA values parameter."""
        # Setup test data
        test_data = pd.DataFrame({'col': [1, None, 3]})
        mock_read_excel.return_value = test_data

        # Mock Excel file behavior
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['Sheet1']
        mock_excel_file.return_value = mock_excel_instance

        # Execute
        self.data_handler.load_file('excel_with_na.xlsx')

        # Verify NA values parameter is passed
        mock_read_excel.assert_called_once_with('excel_with_na.xlsx', sheet_name='Sheet1', na_values=['', 'NA', 'NULL'])

    @patch('pandas.read_csv')
    def test_case_insensitive_extensions(self, mock_read_csv):
        """Test that file extensions are handled case-insensitively."""
        # Setup test data
        test_data = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_csv.return_value = test_data

        # Execute with uppercase extension
        result = self.data_handler.load_file('uppercase_ext.CSV')

        # Assertions
        mock_read_csv.assert_called_once_with('uppercase_ext.CSV', na_values=['', 'NA', 'NULL'])
        self.assertIn('uppercase_ext', self.data_handler.dataframes)

    @patch('pandas.read_csv')
    def test_multiple_file_loads(self, mock_read_csv):
        """Test loading multiple files and ensuring dataframes persist."""
        # Setup test data
        test_data1 = pd.DataFrame({'file1': [1, 2]})
        test_data2 = pd.DataFrame({'file2': [3, 4]})
        mock_read_csv.side_effect = [test_data1, test_data2]

        # Execute
        self.data_handler.load_file('file1.csv')
        self.data_handler.load_file('file2.csv')

        # Assertions
        self.assertEqual(len(self.data_handler.dataframes), 2)
        self.assertIn('file1', self.data_handler.dataframes)
        self.assertIn('file2', self.data_handler.dataframes)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['file1'], test_data1)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['file2'], test_data2)

    @patch('pandas.read_csv')
    def test_dataframes_property_persistence(self, mock_read_csv):
        """Test that dataframes dictionary persists between method calls."""
        # Pre-populate dataframes
        existing_df = pd.DataFrame({'existing': [1, 2, 3]})
        self.data_handler.dataframes['existing_data'] = existing_df

        # Setup new file load
        new_data = pd.DataFrame({'new': [4, 5, 6]})
        mock_read_csv.return_value = new_data

        # Execute
        result = self.data_handler.load_file('new_data.csv')

        # Assertions - both old and new data should exist
        self.assertEqual(len(self.data_handler.dataframes), 2)
        self.assertIn('existing_data', self.data_handler.dataframes)
        self.assertIn('new_data', self.data_handler.dataframes)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['existing_data'], existing_df)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['new_data'], new_data)

    @patch('pandas.read_csv')
    def test_file_path_with_directories(self, mock_read_csv):
        """Test loading file with full path including directories."""
        # Setup test data
        test_data = pd.DataFrame({'data': [1, 2, 3]})
        mock_read_csv.return_value = test_data

        # Execute with full path
        result = self.data_handler.load_file('/home/user/documents/data_file.csv')

        # Assertions - should use just the filename stem
        mock_read_csv.assert_called_once_with('/home/user/documents/data_file.csv', na_values=['', 'NA', 'NULL'])
        self.assertIn('data_file', self.data_handler.dataframes)
        self.mock_logger.info.assert_called_once_with("Successfully loaded CSV file: data_file")

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_excel_sheet_name_formatting(self, mock_read_excel, mock_excel_file):
        """Test that Excel sheet names are stored correctly."""
        # Setup test data
        test_data = pd.DataFrame({'data': [1, 2, 3]})
        mock_read_excel.return_value = test_data

        # Mock Excel file with sheet name containing spaces
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['Data Sheet 1']
        mock_excel_file.return_value = mock_excel_instance

        # Execute
        result = self.data_handler.load_file('test.xlsx')

        # Assertions - sheet name should be stored as-is
        self.assertIn('Data Sheet 1', self.data_handler.dataframes)
        pd.testing.assert_frame_equal(self.data_handler.dataframes['Data Sheet 1'], test_data)

    @patch('pandas.read_csv')
    def test_permission_error(self, mock_read_csv):
        """Test handling of permission errors."""
        # Setup exception
        mock_read_csv.side_effect = PermissionError("Permission denied")

        # Execute and assert exception
        with self.assertRaises(PermissionError):
            self.data_handler.load_file('protected.csv')

        # Verify error logging
        self.mock_logger.error.assert_called_once_with("Error loading file protected.csv: Permission denied")

    @patch('pandas.read_csv')
    def test_empty_file_handling(self, mock_read_csv):
        """Test handling of empty CSV files."""
        # Setup empty dataframe
        empty_df = pd.DataFrame()
        mock_read_csv.return_value = empty_df

        # Execute
        result = self.data_handler.load_file('empty.csv')

        # Assertions
        self.assertIn('empty', self.data_handler.dataframes)
        self.assertTrue(self.data_handler.dataframes['empty'].empty)
        self.mock_logger.info.assert_called_once_with("Successfully loaded CSV file: empty")


class TestDataHandlerInitialization(unittest.TestCase):
    """Test DataHandler initialization."""

    def test_init_with_logger(self):
        """Test DataHandler initialization with logger."""
        mock_logger = Mock()
        handler = DataHandler(mock_logger)

        self.assertEqual(handler.logger, mock_logger)
        self.assertEqual(handler.dataframes, {})

    def test_init_dataframes_empty(self):
        """Test that dataframes dictionary is initialized empty."""
        mock_logger = Mock()
        handler = DataHandler(mock_logger)

        self.assertIsInstance(handler.dataframes, dict)
        self.assertEqual(len(handler.dataframes), 0)

    def test_logger_is_required(self):
        """Test that logger parameter is required."""
        # This should work fine since logger is a required parameter
        mock_logger = Mock()
        handler = DataHandler(mock_logger)
        self.assertIsNotNone(handler.logger)

