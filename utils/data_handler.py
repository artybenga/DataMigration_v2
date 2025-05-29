import pandas as pd
import os
from pathlib import Path


class DataHandler:
    def __init__(self, logger):
        self.logger = logger
        self.dataframes = {}

    def load_file(self, file_path):
        """Load Excel or CSV file and return DataFrame(s)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            file_name = Path(file_path).stem

            if file_ext == '.csv':
                df = pd.read_csv(file_path, na_values=['', 'NA', 'NULL'])
                self.dataframes[file_name] = df
                self.logger.info(f"Successfully loaded CSV file: {file_name}")

            elif file_ext in ['.xlsx', '.xls']:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, na_values=['', 'NA', 'NULL'])
                    sheet_key = f"{sheet_name}"
                    self.dataframes[sheet_key] = df
                self.logger.info(f"Successfully loaded Excel file: {file_name}")

            return self.dataframes

        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            raise

