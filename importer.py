import pandas as pd
import re
from db import get_engine
from logger import log_summary


def sanitize_column_names(columns):
    return [re.sub(r"\s+", "_", col.strip()) for col in columns]


def sanitize_table_name(name):
    return re.sub(r"\s+", "_", name.strip())


def import_dataframes(dfs_dict):
    engine = get_engine()
    summary = []

    for sheet_name, df in dfs_dict.items():
        table_name = sanitize_table_name(sheet_name)
        df.columns = sanitize_column_names(df.columns)

        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False, method="multi")
        summary.append(f"Imported {len(df)} rows into '{table_name}'")

    log_summary(summary)
