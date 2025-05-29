import unittest
import pandas as pd
import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add the directory containing main_window.py to the Python path
current_dir = Path(__file__).parent
main_window_dir = current_dir.parent / "gui"  # Change this if main_window.py is in a different directory
sys.path.insert(0, str(main_window_dir))

# Import the classes to test
try:
    from main_window import ModernFrame, ModernButton, MainWindow
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Looking for main_window.py in: {main_window_dir}")
    print("Please adjust the 'main_window_dir' path in the test file")
    raise


class TestModernFrame(unittest.TestCase):
    """Test cases for ModernFrame class"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication"""
        if cls.app:
            cls.app.quit()

    def test_modern_frame_init_without_title(self):
        """Test ModernFrame initialization without title"""
        frame = ModernFrame()
        self.assertIsNotNone(frame.layout)

        # Convert QMargins to tuple for comparison
        margins = frame.layout.contentsMargins()
        margins_tuple = (margins.left(), margins.top(), margins.right(), margins.bottom())
        self.assertEqual(margins_tuple, (16, 16, 16, 16))

        self.assertEqual(frame.layout.spacing(), 8)

    def test_modern_frame_init_with_title(self):
        """Test ModernFrame initialization with title"""
        title = "Test Frame"
        frame = ModernFrame(title=title)
        self.assertIsNotNone(frame.layout)
        # Check that title label was added
        self.assertGreaterEqual(frame.layout.count(), 1)

    def test_modern_frame_styling(self):
        """Test that ModernFrame has proper styling"""
        frame = ModernFrame()
        style_sheet = frame.styleSheet()
        self.assertIn("background-color: #eaeaea", style_sheet)
        self.assertIn("border-radius: 8px", style_sheet)


class TestModernButton(unittest.TestCase):
    """Test cases for ModernButton class"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication"""
        if cls.app:
            cls.app.quit()

    def test_modern_button_init_default(self):
        """Test ModernButton initialization with default styling"""
        button = ModernButton("Test Button")
        self.assertEqual(button.text(), "Test Button")
        self.assertEqual(button.minimumHeight(), 36)
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)

    def test_modern_button_init_primary(self):
        """Test ModernButton initialization with primary styling"""
        button = ModernButton("Primary Button", primary=True)
        self.assertEqual(button.text(), "Primary Button")
        style_sheet = button.styleSheet()
        self.assertIn("#2962FF", style_sheet)  # Primary color

    def test_modern_button_init_secondary(self):
        """Test ModernButton initialization with secondary styling"""
        button = ModernButton("Secondary Button", primary=False)
        style_sheet = button.styleSheet()
        self.assertIn("#F5F5F5", style_sheet)  # Secondary color


class TestMainWindow(unittest.TestCase):
    """Test cases for MainWindow class"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication"""
        if cls.app:
            cls.app.quit()

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_logger.info = Mock()
        self.mock_logger.error = Mock()
        self.mock_logger.warning = Mock()
        self.mock_logger.addHandler = Mock()

        # Create sample dataframe
        self.sample_dataframe = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })

        # Create main window with mocked database config
        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_main_window_init(self):
        """Test MainWindow initialization"""
        self.assertEqual(self.main_window.logger, self.mock_logger)
        self.assertEqual(self.main_window.dataframes, {})
        self.assertEqual(self.main_window.windowTitle(), "Data Importer")
        self.assertEqual(self.main_window.minimumSize().width(), 1000)
        self.assertEqual(self.main_window.minimumSize().height(), 850)

    def test_main_window_ui_components_exist(self):
        """Test that all UI components are properly initialized"""
        self.assertTrue(hasattr(self.main_window, 'file_label'))
        self.assertTrue(hasattr(self.main_window, 'select_file_btn'))
        self.assertTrue(hasattr(self.main_window, 'df_selector'))
        self.assertTrue(hasattr(self.main_window, 'preview_table'))
        self.assertTrue(hasattr(self.main_window, 'progress_bar'))
        self.assertTrue(hasattr(self.main_window, 'import_btn'))
        self.assertTrue(hasattr(self.main_window, 'log_display'))

    def test_initial_ui_state(self):
        """Test initial state of UI components"""
        self.assertEqual(self.main_window.file_label.text(), "No file selected")
        self.assertFalse(self.main_window.import_btn.isEnabled())
        self.assertFalse(self.main_window.progress_bar.isVisible())
        self.assertTrue(self.main_window.log_display.isReadOnly())

    def test_log_message(self):
        """Test logging functionality"""
        test_message = "Test log message"
        self.main_window.log_message(test_message)
        self.mock_logger.info.assert_called_with(test_message)

    def test_last_directory_initialization(self):
        """Test that last_directory is initialized to home directory"""
        expected_home = str(Path.home())
        self.assertEqual(self.main_window.last_directory, expected_home)


class TestMainWindowFileOperations(unittest.TestCase):
    """Test file operations in MainWindow"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)
        self.sample_dataframe = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })

        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    @patch('main_window.QFileDialog')
    def test_select_file_success(self, mock_file_dialog):
        """Test successful file selection"""
        # Setup mock file dialog
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = True
        mock_dialog_instance.selectedFiles.return_value = ['/path/to/test.csv']
        mock_file_dialog.return_value = mock_dialog_instance

        with patch.object(self.main_window, 'load_file') as mock_load_file:
            self.main_window.select_file()

            self.assertTrue(self.main_window.import_btn.isEnabled())
            self.assertIn("test.csv", self.main_window.file_label.text())
            mock_load_file.assert_called_once_with('/path/to/test.csv')

    @patch('main_window.QFileDialog')
    def test_select_file_cancelled(self, mock_file_dialog):
        """Test cancelled file selection"""
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = False
        mock_file_dialog.return_value = mock_dialog_instance

        with patch.object(self.main_window, 'load_file') as mock_load_file:
            self.main_window.select_file()
            mock_load_file.assert_not_called()

    @patch('pandas.read_csv')
    def test_load_csv_file_success(self, mock_read_csv):
        """Test successful CSV file loading"""
        mock_read_csv.return_value = self.sample_dataframe

        self.main_window.load_file('/path/to/test.csv')

        self.assertIn('CSV Data', self.main_window.dataframes)
        self.assertTrue(self.main_window.dataframes['CSV Data'].equals(self.sample_dataframe))
        mock_read_csv.assert_called_once_with('/path/to/test.csv')

    @patch('pandas.ExcelFile')
    @patch('pandas.read_excel')
    def test_load_excel_file_success(self, mock_read_excel, mock_excel_file):
        """Test successful Excel file loading"""
        # Setup mock Excel file
        mock_excel_instance = Mock()
        mock_excel_instance.sheet_names = ['Sheet1', 'Sheet2']
        mock_excel_file.return_value = mock_excel_instance
        mock_read_excel.return_value = self.sample_dataframe

        self.main_window.load_file('/path/to/test.xlsx')

        self.assertIn('Sheet1', self.main_window.dataframes)
        self.assertIn('Sheet2', self.main_window.dataframes)
        self.assertEqual(mock_read_excel.call_count, 2)

    @patch('pandas.read_csv')
    @patch('main_window.QMessageBox')
    def test_load_file_error(self, mock_message_box, mock_read_csv):
        """Test file loading error handling"""
        mock_read_csv.side_effect = Exception("File not found")

        self.main_window.load_file('/path/to/nonexistent.csv')

        mock_message_box.critical.assert_called_once()

    @patch('main_window.QFileDialog')
    def test_last_directory_update_on_file_selection(self, mock_file_dialog):
        """Test that last_directory is updated when a file is selected"""
        test_file_path = '/some/directory/test.csv'
        expected_directory = '/some/directory'

        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = True
        mock_dialog_instance.selectedFiles.return_value = [test_file_path]
        mock_file_dialog.return_value = mock_dialog_instance

        with patch.object(self.main_window, 'load_file'):
            self.main_window.select_file()
            self.assertEqual(self.main_window.last_directory, expected_directory)


class TestMainWindowPreview(unittest.TestCase):
    """Test preview functionality in MainWindow"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)
        self.sample_dataframe = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })

        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_update_preview_no_dataframes(self):
        """Test update_preview when no dataframes are loaded"""
        self.main_window.dataframes = {}
        self.main_window.update_preview()
        # Should not raise any exceptions
        self.assertEqual(self.main_window.preview_table.rowCount(), 0)

    def test_update_preview_with_data(self):
        """Test update_preview with valid data"""
        self.main_window.dataframes = {'Test Sheet': self.sample_dataframe}
        self.main_window.df_selector.addItem('Test Sheet')
        self.main_window.df_selector.setCurrentText('Test Sheet')

        self.main_window.update_preview()

        self.assertEqual(self.main_window.preview_table.columnCount(), len(self.sample_dataframe.columns))
        self.assertEqual(self.main_window.preview_table.rowCount(), min(10, len(self.sample_dataframe)))

    def test_update_preview_large_dataset(self):
        """Test update_preview with large dataset (more than 10 rows)"""
        large_df = pd.DataFrame({
            'col1': range(20),
            'col2': range(20, 40)
        })
        self.main_window.dataframes = {'Large Sheet': large_df}
        self.main_window.df_selector.addItem('Large Sheet')
        self.main_window.df_selector.setCurrentText('Large Sheet')

        self.main_window.update_preview()

        # Should only show 10 rows maximum
        self.assertEqual(self.main_window.preview_table.rowCount(), 10)


class TestMainWindowImport(unittest.TestCase):
    """Test import functionality in MainWindow"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)
        self.sample_dataframe = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })

        # Create mock database config
        self.mock_db_config = Mock()
        self.mock_db_config.connect.return_value = True
        self.mock_db_config.engine = Mock()
        self.mock_db_config.create_table_from_df.return_value = True

        with patch('main_window.DatabaseConfig', return_value=self.mock_db_config):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    @patch('pandas.DataFrame.to_sql')
    @patch('main_window.QApplication.processEvents')
    def test_import_data_success(self, mock_process_events, mock_to_sql):
        """Test successful data import"""
        # Setup test data
        self.main_window.dataframes = {'Test Sheet': self.sample_dataframe}
        self.main_window.df_selector.addItem('Test Sheet')
        self.main_window.df_selector.setCurrentText('Test Sheet')

        # Mock database operations with proper context manager
        mock_engine = Mock()
        mock_connection = Mock()

        # Create a proper context manager mock
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_connection)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_engine.connect.return_value = mock_context_manager
        self.mock_db_config.engine = mock_engine

        with patch.object(self.main_window, 'show_success_message') as mock_success:
            self.main_window.import_data()

            mock_success.assert_called_once()
            mock_to_sql.assert_called()

    def test_import_data_no_sheet_selected(self):
        """Test import_data when no sheet is selected"""
        self.main_window.dataframes = {}

        with patch('main_window.QMessageBox') as mock_message_box:
            self.main_window.import_data()
            mock_message_box.critical.assert_called()

    def test_import_data_database_connection_failure(self):
        """Test import_data when database connection fails"""
        self.main_window.dataframes = {'Test Sheet': self.sample_dataframe}
        self.main_window.df_selector.addItem('Test Sheet')
        self.main_window.df_selector.setCurrentText('Test Sheet')

        with patch('main_window.DatabaseConfig') as mock_db_class:
            mock_db_instance = Mock()
            mock_db_instance.connect.return_value = False
            mock_db_class.return_value = mock_db_instance

            with patch('main_window.QMessageBox') as mock_message_box:
                self.main_window.import_data()
                mock_message_box.critical.assert_called()

    def test_show_success_message(self):
        """Test success message display"""
        with patch('main_window.QMessageBox') as mock_message_box:
            mock_msg_instance = Mock()
            mock_message_box.return_value = mock_msg_instance

            self.main_window.show_success_message()

            mock_message_box.assert_called_once()
            mock_msg_instance.setText.assert_called_with("Import Completed Successfully!")
            mock_msg_instance.exec.assert_called_once()


class TestMainWindowEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)

        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes"""
        empty_df = pd.DataFrame()
        self.main_window.dataframes = {'Empty Sheet': empty_df}
        self.main_window.df_selector.addItem('Empty Sheet')
        self.main_window.df_selector.setCurrentText('Empty Sheet')

        self.main_window.update_preview()

        self.assertEqual(self.main_window.preview_table.rowCount(), 0)
        self.assertEqual(self.main_window.preview_table.columnCount(), 0)

    def test_dataframe_with_special_characters(self):
        """Test handling of dataframes with special characters in column names"""
        special_df = pd.DataFrame({
            'Column with spaces': [1, 2, 3],
            'Column@with#symbols': [4, 5, 6],
            'Column.with.dots': [7, 8, 9]
        })

        self.main_window.dataframes = {'Special Sheet': special_df}
        self.main_window.df_selector.addItem('Special Sheet')
        self.main_window.df_selector.setCurrentText('Special Sheet')

        self.main_window.update_preview()

        self.assertEqual(self.main_window.preview_table.columnCount(), len(special_df.columns))

    def test_dataframe_with_none_values(self):
        """Test handling of dataframes with None/NaN values"""
        none_df = pd.DataFrame({
            'col1': [1, None, 3],
            'col2': [None, 5, None],
            'col3': [7, 8, 9]
        })

        self.main_window.dataframes = {'None Sheet': none_df}
        self.main_window.df_selector.addItem('None Sheet')
        self.main_window.df_selector.setCurrentText('None Sheet')

        self.main_window.update_preview()

        # Should handle None values without crashing
        self.assertEqual(self.main_window.preview_table.columnCount(), len(none_df.columns))
        self.assertEqual(self.main_window.preview_table.rowCount(), len(none_df))

    def test_resize_event(self):
        """Test window resize event handling"""
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QResizeEvent

        # Create a proper QResizeEvent with old and new sizes
        old_size = QSize(800, 600)
        new_size = QSize(1200, 900)
        resize_event = QResizeEvent(new_size, old_size)

        # This should not raise any exceptions
        self.main_window.resizeEvent(resize_event)


class TestMainWindowIntegration(unittest.TestCase):
    """Integration tests for MainWindow"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)
        self.sample_dataframe = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })

        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_file_selection_to_preview_workflow(self):
        """Test the complete workflow from file selection to preview"""
        # Simulate file loading
        self.main_window.dataframes = {'Test Data': self.sample_dataframe}
        self.main_window.df_selector.clear()
        self.main_window.df_selector.addItems(self.main_window.dataframes.keys())

        # Update preview
        self.main_window.update_preview()

        # Verify preview is populated
        self.assertEqual(self.main_window.preview_table.columnCount(), len(self.sample_dataframe.columns))
        self.assertEqual(self.main_window.preview_table.rowCount(), len(self.sample_dataframe))

    def test_ui_state_progression(self):
        """Test UI state changes throughout the workflow"""
        # Initial state
        self.assertFalse(self.main_window.import_btn.isEnabled())
        self.assertEqual(self.main_window.file_label.text(), "No file selected")

        # After file selection (simulated)
        self.main_window.file_label.setText("test.csv")
        self.main_window.import_btn.setEnabled(True)

        self.assertTrue(self.main_window.import_btn.isEnabled())
        self.assertIn("test.csv", self.main_window.file_label.text())


class TestMainWindowPerformance(unittest.TestCase):
    """Test performance-related scenarios"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = Mock(spec=logging.Logger)

        with patch('main_window.DatabaseConfig'):
            self.main_window = MainWindow(self.mock_logger)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_large_dataframe_preview_performance(self):
        """Test preview performance with large dataframes"""
        # Create a large dataframe
        large_df = pd.DataFrame({
            f'col_{i}': range(1000) for i in range(50)
        })

        self.main_window.dataframes = {'Large Sheet': large_df}
        self.main_window.df_selector.addItem('Large Sheet')
        self.main_window.df_selector.setCurrentText('Large Sheet')

        # This should complete without timeout and only show 10 rows
        self.main_window.update_preview()

        self.assertEqual(self.main_window.preview_table.rowCount(), 10)  # Limited to 10 rows
        self.assertEqual(self.main_window.preview_table.columnCount(), 50)


# Test Suite
def create_test_suite():
    """Create a comprehensive test suite"""
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestModernFrame,
        TestModernButton,
        TestMainWindow,
        TestMainWindowFileOperations,
        TestMainWindowPreview,
        TestMainWindowImport,
        TestMainWindowEdgeCases,
        TestMainWindowIntegration,
        TestMainWindowPerformance
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

