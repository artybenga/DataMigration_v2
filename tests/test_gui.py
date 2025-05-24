import pytest
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication instance"""
    return QApplication([])


@pytest.fixture
def main_window(app, test_logger):
    """Create MainWindow instance"""
    return MainWindow(test_logger)


def test_window_title(main_window):
    """Test window title"""
    assert main_window.windowTitle() == "Data Importer"


def test_initial_state(main_window):
    """Test initial state of GUI elements"""
    assert main_window.file_label.text() == "No file selected"
    assert not main_window.import_btn.isEnabled()
    assert main_window.df_selector.count() == 0


def test_file_selection(main_window, sample_csv_path, qtbot):
    """Test file selection process"""
    # Simulate file selection
    main_window.file_label.setText(str(sample_csv_path))
    main_window.load_file(str(sample_csv_path))

    assert main_window.import_btn.isEnabled()
    assert main_window.df_selector.count() == 1


def test_preview_table(main_window, sample_csv_path, qtbot):
    """Test data preview functionality"""
    main_window.load_file(str(sample_csv_path))

    assert main_window.preview_table.rowCount() > 0
    assert main_window.preview_table.columnCount() > 0


def test_log_display(main_window):
    """Test log display functionality"""
    test_message = "Test log message"
    main_window.log_message(test_message)

    assert test_message in main_window.log_display.toPlainText()