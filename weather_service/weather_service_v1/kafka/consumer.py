# weather_service_v1/kafka/consumer.py

from kafka import KafkaConsumer, KafkaProducer
import json
from weather_service_v1.api.weather import fetch_weather_data
from weather_service_v1.config import Config
from weather_service_v1.logger import setup_logger
from weather_service_v1.utils import preprocess_time

logger = setup_logger(__name__)

class WeatherConsumer:
    def __init__(self, bootstrap_servers=None):
        """Initialize Kafka consumer"""
        if bootstrap_servers is None:
            bootstrap_servers = [Config.KAFKA_BOOTSTRAP_SERVERS]

        self.consumer = KafkaConsumer(
            Config.KAFKA_WEATHER_REQUEST_TOPIC,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='weather_group'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def process_message(self, message):
        """Process a single weather request message"""
        try:
            # Extract request parameters
            request_id = message.get('request_id', 'no-id')  # Get request ID if exists
            latitude = message['latitude']
            longitude = message['longitude']
            date = message['date']
            time_str = message['time']

            # Get the rounded hour
            hour = preprocess_time(time_str)

            # Fetch weather data
            result = fetch_weather_data(latitude, longitude, date, hour)

            # Add request ID to result if it exists
            if request_id != 'no-id':
                result['request_id'] = request_id

            # Send result to results topic
            self.producer.send(Config.KAFKA_WEATHER_RESULT_TOPIC, value=result)
            logger.info(f"Sent result to {Config.KAFKA_WEATHER_RESULT_TOPIC}")

            return result
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_result = {
                'error': str(e),
                'request_id': request_id if request_id != 'no-id' else None
            }
            self.producer.send(Config.KAFKA_WEATHER_RESULT_TOPIC, value=error_result)
            return error_result

    def start_consuming(self):
        """Start consuming messages from Kafka"""
        logger.info("Starting weather data consumer...")
        try:
            for message in self.consumer:
                logger.info(f"Received message: {message.value}")
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
        finally:
            self.close()

    def close(self):
        """Close consumer and producer connections"""
        logger.info("Closing consumer connections...")
        self.consumer.close()
        self.producer.close()