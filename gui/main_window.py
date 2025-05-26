import pandas as pd
import logging
from pathlib import Path
from sqlalchemy import text
from utils.db_config import DatabaseConfig
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QFileDialog, QComboBox,
                            QTableWidget, QTableWidgetItem, QTextEdit,
                            QProgressBar, QMessageBox, QFrame, QScrollArea,
                            QSizePolicy, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from utils.utils import clean_column_name

class ModernFrame(QFrame):
    """A modern styled frame with consistent appearance"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #eaeaea;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(8)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #1565C0;
                    margin-bottom: 8px;
                }
            """)
            self.layout.addWidget(title_label)


class ModernButton(QPushButton):
    """A modern styled button"""

    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        style = """
            QPushButton {
                background-color: %s;
                color: %s;
                border: %s;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: %s;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
                border: none;
            }
        """

        if primary:
            self.setStyleSheet(style % (
                '#2962FF',  # normal background
                'white',  # text color
                'none',  # border
                'bold',  # font weight
                '#1E88E5',  # hover background
                '#1565C0'  # pressed background
            ))
        else:
            self.setStyleSheet(style % (
                '#F5F5F5',  # normal background
                '#424242',  # text color
                '1px solid #E0E0E0',  # border
                'normal',  # font weight
                '#EEEEEE',  # hover background
                '#E0E0E0'  # pressed background
            ))


class MainWindow(QMainWindow):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.db_connect = DatabaseConfig(self.logger)
        self.dataframes = {}
        self.init_ui()
        self.setup_logger()
        self.last_directory = str(Path.home())

    def init_ui(self):
        """Initialize the user interface with modern styling and proper resizing"""
        self.setWindowTitle("Data Importer")
        self.setMinimumSize(1000, 850)

        # Set the main style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                gridline-color: #F5F5F5;
                color: #000000;
            }
            QTableWidget::item {
                color: #000000;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
                color: #000000;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
                color: #000000;
            }
            QComboBox:hover {
                border: 1px solid #2962FF;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QListView {
                background-color: #eaeaea;
                border: 1px solid #E0E0E0;
                padding: 4px;
                selection-color: white;
                selection-background-color: #2962FF;
            }
            QComboBox::item {
                background-color: #eaeaea;
                color: #000000;
            }
            QComboBox::item:hover {
                background-color: #E3F2FD;
            }
            QComboBox::item:selected {
                background-color: #2962FF;
                color: white;
            }
            QLabel {
                color: #424242;
            }
        """)

        # Create main widget and scroll area
        main_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(main_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header section
        header_frame = ModernFrame()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        title = QLabel("Data Importer")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1565C0;
        """)

        description = QLabel("Import your CSV and Excel files into PostgreSQL database")
        description.setStyleSheet("color: #757575; font-size: 14px;")

        header_layout.addWidget(title)
        header_layout.addWidget(description)
        header_frame.layout.addLayout(header_layout)
        layout.addWidget(header_frame)

        # File selection section
        file_frame = ModernFrame("File Selection")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(16)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("""
            color: #757575;
            font-size: 14px;
        """)

        self.select_file_btn = ModernButton("Select File", primary=True)
        self.select_file_btn.clicked.connect(self.select_file)

        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(self.select_file_btn)
        file_frame.layout.addLayout(file_layout)
        layout.addWidget(file_frame)

        # Preview section
        preview_frame = ModernFrame("Data Preview")
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(16)

        # Sheet selector
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(8)

        sheet_label = QLabel("Select Sheet:")
        sheet_label.setStyleSheet("color: #757575; font-size: 14px;")

        self.df_selector = QComboBox()
        self.df_selector.currentIndexChanged.connect(self.update_preview)
        self.df_selector.setMinimumWidth(200)

        selector_layout.addWidget(sheet_label)
        selector_layout.addWidget(self.df_selector)
        selector_layout.addStretch()
        preview_layout.addLayout(selector_layout)

        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        self.preview_table.setMinimumHeight(200)
        preview_layout.addWidget(self.preview_table)

        preview_frame.layout.addLayout(preview_layout)
        layout.addWidget(preview_frame)

        # Import section
        import_frame = ModernFrame("Import")
        import_layout = QVBoxLayout()
        import_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2962FF;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()

        self.import_btn = ModernButton("Import to Database", primary=True)
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.import_data)

        import_layout.addWidget(self.progress_bar)
        import_layout.addWidget(self.import_btn)
        import_frame.layout.addLayout(import_layout)
        layout.addWidget(import_frame)

        # Log section
        log_frame = ModernFrame("Activity Log")
        log_layout = QVBoxLayout()

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(150)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-family: "Consolas", monospace;
                font-size: 13px;
                color: #000000;
            }
        """)

        log_layout.addWidget(self.log_display)
        log_frame.layout.addLayout(log_layout)
        layout.addWidget(log_frame)

    def setup_logger(self):
        """Configure logging to display in the log window"""

        class QTextEditLogger(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget

            def emit(self, record):
                msg = self.format(record)
                self.widget.append(msg)

        log_handler = QTextEditLogger(self.log_display)
        formatter = logging.Formatter('[%(asctime)s UTC] - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # Add user information to the logger
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            return record

        logging.setLogRecordFactory(record_factory)

        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        self.log_message("Application started")

    def select_file(self):
        """Handle file selection with improved dialog"""
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory(self.last_directory)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Data Files (*.csv *.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                self.last_directory = str(Path(file_path).parent)
                self.file_label.setText(str(Path(file_path).name))
                self.import_btn.setEnabled(True)
                self.load_file(file_path)

    def load_file(self, file_path):
        """Load and preview the selected file"""
        try:
            self.dataframes = {}
            file_extension = Path(file_path).suffix.lower()

            if file_extension == '.csv':
                self.dataframes['CSV Data'] = pd.read_csv(file_path)
                self.log_message(f"Loaded CSV file: {file_path}")
            elif file_extension in ['.xlsx', '.xls']:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    self.dataframes[sheet_name] = pd.read_excel(file_path,
                                                                sheet_name=sheet_name)
                self.log_message(f"Loaded Excel file: {file_path} "
                                 f"({len(excel_file.sheet_names)} sheets)")

            # Update the sheet selector
            self.df_selector.clear()
            self.df_selector.addItems(self.dataframes.keys())

            # Update preview
            self.update_preview()

        except Exception as e:
            self.log_message(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def update_preview(self):
        """Update the preview table with improved handling and row limit"""
        if not self.dataframes:
            return

        current_sheet = self.df_selector.currentText()
        if current_sheet not in self.dataframes:
            return

        df = self.dataframes[current_sheet]

        # Clear and prepare the table
        self.preview_table.clear()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(len(df.columns))
        self.preview_table.setHorizontalHeaderLabels(df.columns)

        # Show only first 10 rows
        preview_rows = min(10, len(df))
        self.preview_table.setRowCount(preview_rows)

        # Populate data with explicit black text color
        for row in range(preview_rows):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col])
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                                      Qt.AlignmentFlag.AlignVCenter)
                self.preview_table.setItem(row, col, item)

        # Adjust columns and rows for better display
        self.preview_table.resizeColumnsToContents()
        self.preview_table.resizeRowsToContents()

        # Calculate and set appropriate table height based on content
        header_height = self.preview_table.horizontalHeader().height()
        content_height = sum(self.preview_table.rowHeight(row)
                             for row in range(preview_rows))
        total_height = header_height + content_height + 2
        self.preview_table.setFixedHeight(total_height + 20)

        # Ensure table fills available width
        header = self.preview_table.horizontalHeader()
        header.setStretchLastSection(True)

        self.log_message(f"Updated preview for sheet: {current_sheet} "
                         f"(showing {preview_rows} of {len(df)} rows)")

    def import_data(self):
        """Import data to PostgreSQL database with progress tracking"""
        try:
            # Disable import button and show progress bar
            self.import_btn.setEnabled(False)
            self.progress_bar.show()
            self.progress_bar.setValue(0)

            current_sheet = self.df_selector.currentText()
            if current_sheet not in self.dataframes:
                raise ValueError(f"Sheet {current_sheet} not found in loaded data")

            df = self.dataframes[current_sheet]

            # Generate table name from sheet name
            table_name = clean_column_name(current_sheet)

            # Clean dataframe column names
            df.columns = [clean_column_name(col) for col in df.columns]

            # Initialize database connection using your DatabaseConfig
            db_config = DatabaseConfig(self.logger)

            # Explicit connection check
            if not db_config.connect():
                raise Exception("Failed to establish database connection")

            if db_config.engine is None:
                raise Exception("Database engine not properly initialized")

            self.log_message(f"Starting import of {len(df)} rows to table '{table_name}'")

            try:
                # Verify connection is still valid before creating table
                with db_config.engine.connect() as conn:
                    # Create/Replace table using your existing method
                    if not db_config.create_table_from_df(df, table_name):
                        raise Exception(f"Failed to create table {table_name}")

                    # Update progress to show table creation is complete
                    self.progress_bar.setValue(20)
                    QApplication.processEvents()

                    total_rows = len(df)
                    rows_processed = 0

                    # Process in batches
                    for i in range(0, total_rows, 1000):
                        batch = df.iloc[i:min(i + 1000, total_rows)]

                        try:
                            # Use the same table creation method but with 'append' instead of 'replace'
                            batch.to_sql(table_name, db_config.engine, if_exists='append', index=False)

                            # Update progress
                            rows_processed += len(batch)
                            progress = int((rows_processed / total_rows * 80) + 20)  # 20-100% range
                            self.progress_bar.setValue(progress)
                            QApplication.processEvents()

                        except Exception as e:
                            raise Exception(f"Error importing batch: {str(e)}")

                # Ensure progress bar shows 100%
                self.progress_bar.setValue(100)

                self.log_message(
                    f"Successfully imported {total_rows} rows to table '{table_name}'"
                )

                # Show success message
                self.show_success_message()

            except Exception as e:
                self.log_message(f"Error during import: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import data: {str(e)}"
                )

            finally:
                # Reset UI state
                self.progress_bar.hide()
                self.import_btn.setEnabled(True)

        except Exception as e:
            self.log_message(f"Error preparing import: {str(e)}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to prepare data for import: {str(e)}"
            )
            self.progress_bar.hide()
            self.import_btn.setEnabled(True)

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        if hasattr(self, 'preview_table'):
            self.preview_table.resizeColumnsToContents()
            header = self.preview_table.horizontalHeader()
            header.setStretchLastSection(True)

    def log_message(self, message):
        """Add a message to the log display"""
        self.logger.info(message)

    def show_success_message(self):
        """Show success message with modern styling"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Import Completed Successfully!")
        msg.setWindowTitle("Success")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QPushButton {
                padding: 6px 12px;
                background-color: #2962FF;
                color: white;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1E88E5;
            }
        """)
        msg.exec()

