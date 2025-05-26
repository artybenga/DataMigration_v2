"""
Utilities file for miscellaneous methods
"""

import re


def clean_column_name(column_name: str) -> str:
    """Clean column names by replacing spaces with underscores and removing special characters"""
    # Replace spaces and special characters with underscore
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(column_name))
    # Replace multiple underscores with single underscore
    clean_name = re.sub(r'_+', '_', clean_name)
    # Remove leading/trailing underscores
    clean_name = clean_name.strip('_').lower()
    return clean_name

