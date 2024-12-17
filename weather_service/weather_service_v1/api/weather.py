# weather_service_v1/api/weather.py

import requests
from datetime import datetime
from weather_service_v1.config import Config
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)


def fetch_weather_data(latitude: float, longitude: float, date: str, hour: int) -> dict:
    """
    Fetch weather data from Open-Meteo API for a specific location and hour.

    Args:
        latitude (float): Location latitude
        longitude (float): Location longitude
        date (str): Date in YYYY-MM-DD format
        hour (int): Hour in 24-hour format (0-23)

    Returns:
        dict: Weather data for the specified hour
    """
    logger.info(f"Fetching weather data for coordinates: {latitude}, {longitude} on {date} at {hour:02d}:00")

    url = (
        f"{Config.WEATHER_API_BASE_URL}?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,relative_humidity_2m,rain,snowfall,snow_depth,cloud_cover,wind_speed_10m,wind_direction_10m"
        f"&start_date={date}&end_date={date}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        time_str = f"{date}T{hour:02d}:00"
        hour_index = data['hourly']['time'].index(time_str)

        result = {
            'location_id': 0,
            'time': time_str,
            'temperature': data['hourly']['temperature_2m'][hour_index],
            'relative_humidity': data['hourly']['relative_humidity_2m'][hour_index],
            'rain (mm)': data['hourly']['rain'][hour_index],
            'snowfall (cm)': data['hourly']['snowfall'][hour_index],
            'snow_depth': data['hourly']['snow_depth'][hour_index],
            'cloud_cover': data['hourly']['cloud_cover'][hour_index],
            'wind_speed_10m': data['hourly']['wind_speed_10m'][hour_index],
            'wind_direction_10m (deg)': data['hourly']['wind_direction_10m'][hour_index]
        }

        logger.info("Successfully fetched weather data")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise