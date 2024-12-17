from datetime import datetime


def preprocess_time(time_str: str) -> int:
    """Convert time string to nearest hour"""
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

        return rounded_hour

    except ValueError as e:
        raise ValueError("Invalid time format. Use '3:29 pm', '15:45', or '3:00 PM'") from e