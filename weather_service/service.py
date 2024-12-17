# weather_service/service.py

from kafka import KafkaProducer, KafkaConsumer
import json
import uuid
import time
import logging
from utils import preprocess_time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, kafka_server='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.consumer = KafkaConsumer(
            'model_results',
            bootstrap_servers=[kafka_server],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id=f'weather_client_{uuid.uuid4()}',
            consumer_timeout_ms=1000
        )

    def get_weather(self, latitude: float, longitude: float, date: str, time_str: str,
                   timeout_seconds: int = 30) -> dict:
        request_id = str(uuid.uuid4())
        hour = preprocess_time(time_str)
        message = {
            'request_id': request_id,
            'latitude': latitude,
            'longitude': longitude,
            'date': date,
            'hour': hour
        }

        self.producer.send('weather_requests', message)
        self.producer.flush()

        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                for msg in self.consumer:
                    logger.info(f"Received message: {msg.value}")
                    if msg.value.get('request_id') == request_id:
                        if 'error' in msg.value:
                            raise Exception(msg.value['error'])
                        return msg.value
            except StopIteration:
                continue

        raise TimeoutError(f"No response received within {timeout_seconds} seconds")

    def close(self):
        self.producer.close()
        self.consumer.close()