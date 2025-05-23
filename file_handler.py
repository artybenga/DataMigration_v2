import pandas as pd
import os

def read_file(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".csv":
        return {os.path.splitext(os.path.basename(filepath))[0]: pd.read_csv(filepath)}
    elif ext in [".xls", ".xlsx"]:
        excel = pd.read_excel(filepath, sheet_name=None)
        return {sheet: df for sheet, df in excel.items()}
    else:
        raise ValueError("Unsupported file type")
