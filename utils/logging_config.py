# logging_config.py
import logging
import os
import pytz
from datetime import datetime

def get_logger(name):
    # Get the current working directory
    cwd = os.getcwd()

    # Create a file handler and set the mode to 'w' to purge the log file
    file_handler = logging.FileHandler(os.path.join(cwd, 'app.log'), mode='w')
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter with the timestamp in IST timezone
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')
    file_handler.setFormatter(formatter)

    # Create a logger with the given name and add the file handler
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger