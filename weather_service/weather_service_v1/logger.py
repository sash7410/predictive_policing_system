# weather_service_v1/logger.py

import logging
import sys
from weather_service_v1.config import Config


def setup_logger(name):
    """Configure and return a logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger