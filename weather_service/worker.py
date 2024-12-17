from kafka import KafkaConsumer, KafkaProducer
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherWorker:
    def __init__(self, kafka_server='localhost:9092'):
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
            'humidity': data['hourly']['relative_humidity_2m'][hour_index],
            'rain': data['hourly']['rain'][hour_index],
            'wind_speed': data['hourly']['wind_speed_10m'][hour_index],
            'wind_direction': data['hourly']['wind_direction_10m'][hour_index]
        }

    def start(self):
        logger.info("Weather worker started...")
        try:
            for message in self.consumer:
                data = message.value
                request_id = data.get('request_id')
                try:
                    result = self.fetch_weather(
                        data['latitude'],
                        data['longitude'],
                        data['date'],
                        data['hour']
                    )
                    result['request_id'] = request_id
                    self.producer.send('weather_results', result)

                except Exception as e:
                    error_msg = {'error': str(e), 'request_id': request_id}
                    self.producer.send('weather_results', error_msg)
                self.producer.flush()
        finally:
            self.close()

    def close(self):
        self.consumer.close()
        self.producer.close()


if __name__ == "__main__":
    worker = WeatherWorker()
    worker.start()