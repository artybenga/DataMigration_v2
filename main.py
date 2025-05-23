import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox
)
from file_handler import read_file
from importer import import_dataframes

class ImporterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel/CSV to PostgreSQL Importer")
        self.setGeometry(100, 100, 500, 200)

        layout = QVBoxLayout()
        self.label = QLabel("Choose a CSV or Excel file to import")
        self.import_button = QPushButton("Select File")

        self.import_button.clicked.connect(self.load_file)

        layout.addWidget(self.label)
        layout.addWidget(self.import_button)
        self.setLayout(layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV/Excel Files (*.csv *.xls *.xlsx)")
        if file_path:
            try:
                self.label.setText(f"Processing: {file_path}")
                dfs = read_file(file_path)
                import_dataframes(dfs)
                QMessageBox.information(self, "Success", "Data imported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            self.label.setText("No file selected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImporterGUI()
    window.show()
    sys.exit(app.exec())
