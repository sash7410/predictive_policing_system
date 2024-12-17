# weather_service_v1/utils/time.py

from datetime import datetime
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)


def preprocess_time(time_str: str) -> int:
    """
    Convert time string to nearest hour using round function.
    Accepts formats like "3:29 pm", "15:45", "3:00 PM", etc.

    Args:
        time_str (str): Time string in various formats

    Returns:
        int: Rounded hour in 24-hour format (0-23)
    """
    try:
        # Try parsing with AM/PM
        try:
            dt = datetime.strptime(time_str.strip().lower(), "%I:%M %p")
        except ValueError:
            # Try parsing 24-hour format
            try:
                dt = datetime.strptime(time_str.strip(), "%H:%M")
            except ValueError:
                # Try parsing with AM/PM without space
                dt = datetime.strptime(time_str.strip().lower(), "%I:%M%p")

        # Convert to decimal hours and round to nearest hour
        decimal_hour = dt.hour + dt.minute / 60
        rounded_hour = round(decimal_hour)

        # Handle midnight case
        if rounded_hour == 24:
            rounded_hour = 0

        logger.info(f"Preprocessed time {time_str} to {rounded_hour:02d}:00")
        return rounded_hour

    except ValueError as e:
        logger.error(f"Invalid time format: {time_str}")
        raise ValueError(
            "Invalid time format. Please use formats like '3:29 pm', '15:45', or '3:00 PM'"
        ) from e