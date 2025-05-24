# Data Importer

A Python application for importing CSV and Excel files into PostgreSQL databases with data preview and logging capabilities.

## Features

- Modern PyQt6-based GUI interface
- Support for both CSV and Excel file imports
- Automatic table creation based on DataFrame structure
- Preview of data (first 10 rows) before import
- Comprehensive logging system with both file and GUI display
- Multiple worksheet handling for Excel files
- Automatic handling of NULL/NaN values
- Clean column name formatting (spaces replaced with underscores)
- Table naming based on source file/sheet names
- Environment-based configuration
- Progress tracking through GUI

## Prerequisites

- Python 3.7 or higher
- PostgreSQL database
- pip (Python package installer)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd data_importer
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure your database connection:
   - Rename `.env.example` to `.env`
   - Update the values in `.env` with your PostgreSQL credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

## Project Structure
```
data_importer/
├── main.py               # Application entry point
├── .env                 # Environment configuration
├── requirements.txt     # Python dependencies
├── gui/                # GUI package
│   ├── __init__.py
│   └── main_window.py  # Main application window
└── utils/              # Utility package
    ├── __init__.py
    ├── data_handler.py # File loading and processing
    ├── db_config.py    # Database configuration
    └── logger_config.py # Logging setup
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Using the application:
   - Click "Select File" to choose a CSV or Excel file
   - Preview the data in the table view
   - If the file contains multiple sheets (Excel), use the dropdown to switch between them
   - Click "Import to Database" to start the import process
   - Monitor the progress in the log display

3. Logging:
   - Logs are saved to `data_import_YYYYMMDD_HHMMSS.log`
   - Log files contain timestamps (UTC), log levels, and detailed operation information
   - The GUI displays real-time log updates

## Data Handling

- **CSV Files**: Imported as single tables
- **Excel Files**: Each worksheet creates a separate table
- **Column Names**: Spaces are replaced with underscores
- **NULL Values**: Empty cells, 'NA', and 'NULL' are converted to NULL in the database
- **Table Names**: Generated from file names (CSV) or sheet names (Excel)

## Error Handling

The application includes comprehensive error handling for:
- File loading issues
- Database connection problems
- Data type mismatches
- Import failures

All errors are logged both to file and displayed in the GUI.

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

N/A (For now - 20250524)

## Support

For support, please create an issue in the repository or contact the maintainers.

## Authors

- Initial work - Arthur Bengasino

## Acknowledgments

- PyQt6 for the GUI framework
- pandas for data handling
- SQLAlchemy for database operations

## Last Updated

2025-05-24 07:22:09 UTC by @artybenga