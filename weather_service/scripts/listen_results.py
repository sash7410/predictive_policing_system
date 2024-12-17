# scripts/listen_results.py

from kafka import KafkaConsumer
import json
from weather_service_v1.config import Config
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)


def listen_for_results():
    """Listen for weather results from Kafka"""
    consumer = KafkaConsumer(
        Config.KAFKA_WEATHER_RESULT_TOPIC,
        bootstrap_servers=[Config.KAFKA_BOOTSTRAP_SERVERS],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest'
    )

    logger.info("Starting to listen for weather results...")
    try:
        for message in consumer:
            result = message.value
            print("\nReceived Weather Data:")
            print("-" * 50)
            for key, value in result.items():
                print(f"{key}: {value}")
            print("-" * 50)
    except KeyboardInterrupt:
        logger.info("Stopping result listener...")
    finally:
        consumer.close()


if __name__ == "__main__":
    listen_for_results()