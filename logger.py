import logging
from datetime import datetime

log_file = f"import.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def log_summary(summary_lines):
    for line in summary_lines:
        logging.info(line)
    print("\n".join(summary_lines))
