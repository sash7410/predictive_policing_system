# weather_service_v1/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    WEATHER_API_BASE_URL = os.getenv('WEATHER_API_BASE_URL', 'https://api.open-meteo.com/v1/forecast')
    KAFKA_WEATHER_REQUEST_TOPIC = os.getenv('KAFKA_WEATHER_REQUEST_TOPIC', 'weather_requests')
    KAFKA_WEATHER_RESULT_TOPIC = os.getenv('KAFKA_WEATHER_RESULT_TOPIC', 'weather_results')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')