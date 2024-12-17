from kafka import KafkaConsumer, KafkaProducer
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherWorker:
    def __init__(self, kafka_server='localhost:9092', fastapi_url="http://localhost:5002/predict"):
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

        self.fastapi_url = fastapi_url

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
        Send weather data to FastAPI for prediction.
        """
        try:
            response = requests.post(self.fastapi_url, json=weather_data)
            response.raise_for_status()
            return response.json()  # Prediction result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling FastAPI service: {e}")
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

                    # Send weather data to FastAPI for prediction
                    prediction_result = self.get_prediction(weather_data)

                    # Append request_id to prediction result
                    prediction_result['request_id'] = request_id

                    # Send the prediction result to Kafka topic
                    self.producer.send('weather_results', prediction_result)
                    self.producer.flush()

                    logger.info(f"Prediction sent to Kafka: {prediction_result}")

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
    worker = WeatherWorker()
    worker.start()
