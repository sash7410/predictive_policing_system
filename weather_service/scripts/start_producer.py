# scripts/start_producer.py

from weather_service_v1.kafka.producer import WeatherProducer
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)

def main():
    producer = WeatherProducer()
    try:
        # Example usage
        producer.send_weather_request(
            latitude=40.87922,
            longitude=-73.86106,
            date="2024-12-17",
            time_str="3:45 PM"
        )
        logger.info("Weather request sent successfully")
    except Exception as e:
        logger.error(f"Error sending weather request: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()