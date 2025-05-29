import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger_config import setup_logger


def main():
    # Setup logging
    current_time = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/data_import_{current_time}.log'
    logger = setup_logger(log_file)

    logger.info("Application started")

    try:
        app = QApplication(sys.argv)
        window = MainWindow(logger)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    main()