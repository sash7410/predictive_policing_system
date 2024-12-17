# test_weather_service.py

from weather_service_v1.kafka.producer import WeatherProducer
from weather_service_v1 import setup_logger
import time

logger = setup_logger(__name__)


def test_weather_service():
    """Test the weather service with synchronous request-response"""
    producer = WeatherProducer()

    try:
        # Test multiple locations and times
        test_cases = [
            {
                'latitude': 40.87922,
                'longitude': -73.86106,
                'date': "2024-12-17",
                'time_str': "3:45 PM",
                'description': "New York"
            },
            {
                'latitude': 34.0522,
                'longitude': -118.2437,
                'date': "2024-12-17",
                'time_str': "2:30 PM",
                'description': "Los Angeles"
            }
        ]

        for case in test_cases:
            logger.info(f"\nTesting weather data for {case['description']}:")

            result = producer.get_weather_data(
                latitude=case['latitude'],
                longitude=case['longitude'],
                date=case['date'],
                time_str=case['time_str']
            )

            # Print the results
            logger.info(f"Location: {case['description']}")
            logger.info(f"Time: {result['time']}")
            logger.info(f"Temperature: {result['temperature']}°C")
            logger.info(f"Humidity: {result['relative_humidity']}%")
            logger.info(f"Wind Speed: {result['wind_speed_10m']} km/h")
            logger.info(f"Wind Direction: {result['wind_direction_10m (deg)']}°")
            logger.info("------------------------")

            # Small delay between requests
            time.sleep(1)

    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    test_weather_service()