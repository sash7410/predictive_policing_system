# Weather Service

A weather service that uses Kafka to process weather data requests from the Open-Meteo API.

## Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e ".[dev]"
```

## Usage

1. Start Kafka using Docker:
```bash
docker-compose up -d
```

2. Run the consumer:
```bash
python scripts/start_consumer.py
```

3. In another terminal, run the producer:
```bash
python scripts/start_producer.py
```

## Configuration

Configuration can be set via environment variables in `.env` file:
- KAFKA_BOOTSTRAP_SERVERS: Kafka server address (default: localhost:9092)
- WEATHER_API_BASE_URL: OpenMeteo API URL
- LOG_LEVEL: Logging level (default: INFO)