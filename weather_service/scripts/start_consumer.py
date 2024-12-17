# scripts/start_consumer.py

from weather_service_v1.kafka.consumer import WeatherConsumer
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)

def main():
    consumer = WeatherConsumer()
    try:
        logger.info("Starting weather consumer...")
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()