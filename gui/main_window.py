from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QTableWidget,
                             QTableWidgetItem, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt
from utils.data_handler import DataHandler
from utils.db_config import DatabaseConfig
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.data_handler = DataHandler(logger)
        self.db_config = DatabaseConfig(logger)
        self.current_dataframes = {}

        self.setWindowTitle("Data Importer")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # File selection section
        file_section = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.select_file)
        file_section.addWidget(self.file_label)
        file_section.addWidget(select_file_btn)

        # DataFrame selector
        self.df_selector = QComboBox()
        self.df_selector.currentIndexChanged.connect(self.update_preview)

        # Preview table
        self.preview_table = QTableWidget()

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        # Import button
        self.import_btn = QPushButton("Import to Database")
        self.import_btn.clicked.connect(self.import_to_db)
        self.import_btn.setEnabled(False)

        # Add widgets to layout
        layout.addLayout(file_section)
        layout.addWidget(self.df_selector)
        layout.addWidget(QLabel("Data Preview (First 10 rows):"))
        layout.addWidget(self.preview_table)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_display)
        layout.addWidget(self.import_btn)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Data Files (*.csv *.xlsx *.xls)"
        )

        if file_path:
            self.file_label.setText(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            self.current_dataframes = self.data_handler.load_file(file_path)
            self.df_selector.clear()
            self.df_selector.addItems(self.current_dataframes.keys())
            self.import_btn.setEnabled(True)
            self.log_message(f"Successfully loaded file: {file_path}")
            self.update_preview()
        except Exception as e:
            self.log_message(f"Error loading file: {str(e)}", "ERROR")

    def update_preview(self):
        if not self.df_selector.currentText():
            return

        df = self.current_dataframes[self.df_selector.currentText()]
        self.preview_table.setRowCount(min(10, len(df)))
        self.preview_table.setColumnCount(len(df.columns))
        self.preview_table.setHorizontalHeaderLabels(df.columns)

        for i in range(min(10, len(df))):
            for j in range(len(df.columns)):
                value = str(df.iloc[i, j])
                self.preview_table.setItem(i, j, QTableWidgetItem(value))

    def import_to_db(self):
        if not self.db_config.connect():
            self.log_message("Failed to connect to database", "ERROR")
            return

        for name, df in self.current_dataframes.items():
            table_name = name.lower().replace(' ', '_')
            if self.db_config.create_table_from_df(df, table_name):
                self.log_message(f"Successfully imported {name} to table {table_name}")
            else:
                self.log_message(f"Failed to import {name}", "ERROR")

    def log_message(self, message, level="INFO"):
        self.log_display.append(f"{level}: {message}")