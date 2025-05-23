import pandas as pd
import os

def read_file(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath, keep_default_na=True, na_values=[""])
        return {os.path.splitext(os.path.basename(filepath))[0]: clean_dataframe(df)}
    elif ext in [".xls", ".xlsx"]:
        excel = pd.read_excel(filepath, sheet_name=None, keep_default_na=True, na_values=[""])
        return {sheet: clean_dataframe(df) for sheet, df in excel.items()}
    else:
        raise ValueError("Unsupported file type")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Strip spaces from column names
    df.columns = [col.strip() for col in df.columns]

    # Convert NaN and NaT to None for proper SQL NULL insertion
    return df.where(pd.notnull(df), None)
