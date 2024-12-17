from kafka import KafkaProducer, KafkaConsumer
import json
import uuid
import time
import logging
from threading import Lock, Thread
from queue import Queue
from typing import Dict, Optional

from weather_service.utils import preprocess_time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self, kafka_server='localhost:9092'):
        self.kafka_server = kafka_server
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Create a persistent consumer with a stable group ID
        self.consumer = KafkaConsumer(
            'weather_results',
            bootstrap_servers=[kafka_server],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='weather_service_consumer',
            enable_auto_commit=True
        )

        # Thread-safe storage for pending requests and their results
        self.pending_requests: Dict[str, Queue] = {}
        self.request_lock = Lock()

        # Start the response processing thread
        self.running = True
        self.response_thread = Thread(target=self._process_responses, daemon=True)
        self.response_thread.start()

    def _process_responses(self):
        """Background thread to continuously process responses."""
        while self.running:
            try:
                message_batch = self.consumer.poll(timeout_ms=100)
                for tp, messages in message_batch.items():
                    for message in messages:
                        request_id = message.value.get('request_id')
                        if request_id:
                            with self.request_lock:
                                if request_id in self.pending_requests:
                                    self.pending_requests[request_id].put(message.value)
            except Exception as e:
                logger.error(f"Error processing responses: {e}")
                continue

    def get_weather(self, latitude: float, longitude: float, date: str, time_str: str,
                    timeout_seconds: int = 30) -> dict:
        request_id = str(uuid.uuid4())
        hour = preprocess_time(time_str)

        # Create result queue for this request
        result_queue = Queue()
        with self.request_lock:
            self.pending_requests[request_id] = result_queue

        try:
            # Send request
            message = {
                'request_id': request_id,
                'latitude': latitude,
                'longitude': longitude,
                'date': date,
                'hour': hour
            }
            self.producer.send('weather_requests', message)
            self.producer.flush()
            logger.info(f"Sent request: {request_id}")

            # Wait for response
            try:
                result = result_queue.get(timeout=timeout_seconds)
                if 'error' in result:
                    raise Exception(result['error'])
                print("lolol")
                print(result)
                return result
            except Queue.Empty:
                raise TimeoutError(f"No response received within {timeout_seconds} seconds")

        finally:
            # Clean up request state
            with self.request_lock:
                self.pending_requests.pop(request_id, None)

    def close(self):
        """Gracefully shut down the service."""
        self.running = False
        if self.response_thread.is_alive():
            self.response_thread.join(timeout=5)
        self.producer.close()
        self.consumer.close()
        logger.info("Weather service shut down.")