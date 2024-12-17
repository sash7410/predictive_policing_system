import os
import uuid
import time
from kafka import KafkaConsumer, KafkaProducer
import json
import requests
import logging
from threading import Lock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherWorker:
    def __init__(self, kafka_server='localhost:9092'):
        self.kafka_server = kafka_server
        self.consumer = KafkaConsumer(
            'weather_requests',
            bootstrap_servers=[kafka_server],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='weather_workers'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Create a persistent model results consumer
        self.model_consumer = KafkaConsumer(
            'model_results',
            bootstrap_servers=[kafka_server],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='weather_model_consumer',
            enable_auto_commit=True
        )

        self.response_lock = Lock()
        self.pending_requests = {}

    def fetch_weather(self, latitude: float, longitude: float, date: str, hour: int) -> dict:
        """
        Fetch weather data from the Open-Meteo API.
        """
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&hourly=temperature_2m,relative_humidity_2m,rain,snowfall,snow_depth,"
            f"cloud_cover,wind_speed_10m,wind_direction_10m"
            f"&start_date={date}&end_date={date}"
        )
        print(url)
        print("lolololol")

        response = requests.get(url)
        data = response.json()

        time_str = f"{date}T{hour:02d}:00"
        hour_index = data['hourly']['time'].index(time_str)

        d_ = {
            'temperature': data['hourly']['temperature_2m'][hour_index],
            'relative_humidity': data['hourly']['relative_humidity_2m'][hour_index],
            'rain': data['hourly']['rain'][hour_index],
            'snowfall': data['hourly']['snowfall'][hour_index],
            'snow_depth': data['hourly']['snow_depth'][hour_index],
            'cloud_cover': data['hourly']['cloud_cover'][hour_index],
            'wind_speed_10m': data['hourly']['wind_speed_10m'][hour_index],
            'wind_direction_10m': data['hourly']['wind_direction_10m'][hour_index],
            'Latitude': latitude,
            'Longitude': longitude,
            'date': date,
            'time': f"{hour:02d}:00"
        }
        print(d_)
        return d_

    def get_prediction(self, weather_data: dict) -> dict:
        """Send weather data to model service and wait for response."""
        try:
            request_id = str(uuid.uuid4())
            weather_data['request_id'] = request_id

            # Register the request before sending
            with self.response_lock:
                self.pending_requests[request_id] = None

            # Send to model_requests topic
            self.producer.send('model_requests', weather_data)
            self.producer.flush()
            logger.info(f"Sent request to model service: {request_id}")

            # Wait for response
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                with self.response_lock:
                    if self.pending_requests[request_id] is not None:
                        result = self.pending_requests[request_id]
                        del self.pending_requests[request_id]
                        return result
                time.sleep(0.1)  # Short sleep to prevent CPU spinning

            # Cleanup on timeout
            with self.response_lock:
                del self.pending_requests[request_id]
            return {"error": "Timeout waiting for model prediction", "request_id": request_id}

        except Exception as e:
            logger.error(f"Error in get_prediction: {e}")
            return {"error": str(e), "request_id": request_id}

    def process_model_responses(self):
        """Background thread to process model responses."""
        try:
            while True:
                message_batch = self.model_consumer.poll(timeout_ms=100)
                for tp, messages in message_batch.items():
                    for message in messages:
                        request_id = message.value.get('request_id')
                        if request_id:
                            with self.response_lock:
                                if request_id in self.pending_requests:
                                    self.pending_requests[request_id] = message.value
        except Exception as e:
            logger.error(f"Error processing model responses: {e}")

    def start(self):
        """Start the weather worker."""
        logger.info("Weather worker started...")

        # Start processing model responses in a separate thread
        from threading import Thread
        response_thread = Thread(target=self.process_model_responses, daemon=True)
        response_thread.start()

        try:
            for message in self.consumer:
                data = message.value
                request_id = data.get('request_id')
                logger.info(f"Received request with ID: {request_id}")

                try:
                    weather_data = self.fetch_weather(
                        data['latitude'],
                        data['longitude'],
                        data['date'],
                        data['hour']
                    )
                    weather_data['request_id'] = request_id

                    prediction_result = self.get_prediction(weather_data)
                    prediction_result['request_id'] = request_id

                    logger.info(f"Prediction result: {prediction_result}")
                    self.producer.send('weather_results', prediction_result)
                    self.producer.flush()
                    logger.info(f"Sent result for request ID: {request_id}")

                except Exception as e:
                    error_msg = {'error': str(e), 'request_id': request_id}
                    self.producer.send('weather_results', error_msg)
                    self.producer.flush()
                    logger.error(f"Error processing request {request_id}: {e}")

        finally:
            self.close()

    def close(self):
        """Gracefully close Kafka consumers and producer."""
        self.consumer.close()
        self.model_consumer.close()
        self.producer.close()
        logger.info("Weather worker shut down.")


if __name__ == "__main__":
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"Connecting to Kafka at: {kafka_server}")
    worker = WeatherWorker(kafka_server=kafka_server)
    worker.start()