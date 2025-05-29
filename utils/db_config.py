import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np


class DatabaseConfig:
    def __init__(self, logger):
        load_dotenv()
        self.logger = logger
        self.engine = None

    def get_connection_string(self):
        return (f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

    def connect(self):
        try:
            self.engine = create_engine(self.get_connection_string())
            self.logger.info("Successfully connected to database")
            return True
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            return False

    def create_table_from_df(self, df, table_name):
        """Create table based on DataFrame structure"""
        # Clean column names
        df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]

        # Replace NaT/NaN with None more explicitly
        df = df.replace({pd.NaT: None, np.nan: None})

        # Additional cleanup to ensure all NaN-like values become None
        for col in df.columns:
            df[col] = df[col].where(pd.notnull(df[col]), None)

        try:
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            self.logger.info(f"Successfully created table: {table_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating table {table_name}: {str(e)}")
            return False

