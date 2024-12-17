# weather_service_v1/kafka/__init__.py

from .producer import WeatherProducer
from .consumer import WeatherConsumer

__all__ = ['WeatherProducer', 'WeatherConsumer']