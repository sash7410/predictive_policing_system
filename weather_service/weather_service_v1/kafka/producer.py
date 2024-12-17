# weather_service_v1/kafka/producer.py

from kafka import KafkaProducer, KafkaConsumer
import json
import uuid
import time
from weather_service_v1.config import Config
from weather_service_v1.logger import setup_logger

logger = setup_logger(__name__)


class WeatherProducer:
    def __init__(self, bootstrap_servers=None):
        """Initialize Kafka producer"""
        if bootstrap_servers is None:
            bootstrap_servers = [Config.KAFKA_BOOTSTRAP_SERVERS]

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Initialize consumer for results
        self.consumer = KafkaConsumer(
            Config.KAFKA_WEATHER_RESULT_TOPIC,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id=f'weather_client_{uuid.uuid4()}'  # Unique consumer group
        )

    def get_weather_data(self, latitude: float, longitude: float, date: str, time_str: str,
                         timeout_seconds: int = 30) -> dict:
        """
        Send weather request and wait for result synchronously.

        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            date (str): Date in YYYY-MM-DD format
            time_str (str): Time string (e.g., "3:45 PM")
            timeout_seconds (int): How long to wait for response

        Returns:
            dict: Weather data result
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        message = {
            'request_id': request_id,
            'latitude': latitude,
            'longitude': longitude,
            'date': date,
            'time': time_str
        }

        try:
            # Send request
            future = self.producer.send(Config.KAFKA_WEATHER_REQUEST_TOPIC, value=message)
            future.get(timeout=10)  # Wait for message to be sent
            logger.info(f"Sent weather request: {message}")

            # Wait for matching response
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                msg = next(self.consumer, None)
                if msg is None:
                    continue

                result = msg.value
                if result.get('request_id') == request_id:
                    logger.info("Received matching weather result")
                    return result

            raise TimeoutError(f"No response received after {timeout_seconds} seconds")

        except Exception as e:
            logger.error(f"Error in weather request: {e}")
            raise

    def send_weather_request(self, latitude: float, longitude: float, date: str, time_str: str):
        """Send weather request to Kafka topic (async version)"""
        message = {
            'latitude': latitude,
            'longitude': longitude,
            'date': date,
            'time': time_str
        }

        try:
            future = self.producer.send(Config.KAFKA_WEATHER_REQUEST_TOPIC, value=message)
            future.get(timeout=10)  # Wait for message to be sent
            logger.info(f"Sent weather request: {message}")
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")
            raise

    def close(self):
        """Close the producer and consumer connections"""
        self.producer.close()
        if hasattr(self, 'consumer'):
            self.consumer.close()