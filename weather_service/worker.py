import os
import uuid
import time  # Correct import
from kafka import KafkaConsumer, KafkaProducer
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherWorker:
    def __init__(self, kafka_server='localhost:9092'):
        self.kafka_server = kafka_server  # Store kafka_server
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

        response = requests.get(url)
        data = response.json()

        time_str = f"{date}T{hour:02d}:00"
        hour_index = data['hourly']['time'].index(time_str)

        return {
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

    def get_prediction(self, weather_data: dict) -> dict:
        """
        Send weather data to model service via Kafka and wait for response.
        """
        try:
            request_id = str(uuid.uuid4())
            weather_data['request_id'] = request_id

            # Create a consumer for model results
            model_consumer = KafkaConsumer(
                'model_results',
                bootstrap_servers=[self.kafka_server],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                group_id=f'weather_worker_{uuid.uuid4()}',
                consumer_timeout_ms=1000
            )

            # Send to model_requests topic
            self.producer.send('model_requests', weather_data)
            self.producer.flush()
            logger.info(f"Sent request to model service: {request_id}")

            # Wait for response
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                try:
                    message_batch = model_consumer.poll(timeout_ms=1000)
                    for tp, messages in message_batch.items():
                        for message in messages:
                            if message.value.get('request_id') == request_id:
                                model_consumer.close()
                                return message.value
                except Exception as e:
                    logger.error(f"Error polling messages: {e}")

            model_consumer.close()
            return {"error": "Timeout waiting for model prediction"}

        except Exception as e:
            logger.error(f"Error in get_prediction: {e}")
            return {"error": str(e)}

    def start(self):
        """
        Consume weather_requests, fetch weather, send to FastAPI, and publish prediction results.
        """
        logger.info("Weather worker started...")
        try:
            for message in self.consumer:
                data = message.value
                request_id = data.get('request_id')

                try:
                    # Fetch weather data
                    weather_data = self.fetch_weather(
                        data['latitude'],
                        data['longitude'],
                        data['date'],
                        data['hour']
                    )

                    weather_data['request_id'] = request_id

                    # Get prediction from model service
                    prediction_result = self.get_prediction(weather_data)

                    # Send the result back
                    self.producer.send('weather_results', prediction_result)
                    self.producer.flush()
                    logger.info(f"Sent result: {prediction_result}")

                except Exception as e:
                    error_msg = {'error': str(e), 'request_id': request_id}
                    self.producer.send('weather_results', error_msg)
                    self.producer.flush()
                    logger.error(f"Error processing request: {e}")

        finally:
            self.close()

    def close(self):
        """
        Gracefully close Kafka consumer and producer.
        """
        self.consumer.close()
        self.producer.close()
        logger.info("Weather worker shut down.")

if __name__ == "__main__":
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"Connecting to Kafka at: {kafka_server}")  # Debug print
    worker = WeatherWorker(kafka_server=kafka_server)
    worker.start()