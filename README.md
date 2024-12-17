# Predictive Policing System

A system that combines weather data with machine learning to predict crime probabilities. The system uses Kafka for message queuing, PySpark for ML predictions, and integrates with the Open-Meteo API for weather data.

## System Architecture

The system consists of three main components:
- Weather Service: Fetches weather data from Open-Meteo API
- ML Model Service: Processes weather data to make crime predictions
- Kafka Message Queue: Handles communication between services

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Java 11 (for PySpark)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd predictive_policing_system
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the System

1. Start Kafka and all services using Docker:
```bash
docker-compose up -d
```

2. Initialize Kafka topics:
```bash
docker exec predictive_policing_system-kafka-1 kafka-topics --create --topic weather_requests --bootstrap-server localhost:9092
docker exec predictive_policing_system-kafka-1 kafka-topics --create --topic weather_results --bootstrap-server localhost:9092
docker exec predictive_policing_system-kafka-1 kafka-topics --create --topic model_requests --bootstrap-server localhost:9092
docker exec predictive_policing_system-kafka-1 kafka-topics --create --topic model_results --bootstrap-server localhost:9092
```

3. Run each component (in separate terminals):

```bash
# Terminal 1 - Start the ML Model Server
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 python -m ml_model.serve_model

# Terminal 2 - Start the Weather Worker
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 python -m weather_service.worker

# Terminal 3 - Run test client
python weather_service/test_weather.py
```

## Project Structure

```
predictive_policing_system/
├── ml_model/
│   ├── crime_prediction_model/   # ML model files
│   ├── serve_model.py           # ML model server
│   └── Dockerfile
├── weather_service/
│   ├── worker.py               # Weather data processor
│   ├── service.py             # Weather service client
│   └── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

Environment variables can be set in `.env` file:
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (default: localhost:9092)
- `WEATHER_API_BASE_URL`: OpenMeteo API URL
- `MODEL_PATH`: Path to ML model files

## API Usage

To use the weather prediction service:

```python
from weather_service.service import WeatherService

weather = WeatherService()
result = weather.get_weather(
    latitude=40.87922,
    longitude=-73.86106,
    date="2024-12-17",
    time_str="3:45 PM"
)
print(result)
```

## Monitoring

Monitor Kafka topics:
```bash
# View messages in any topic
docker exec -it predictive_policing_system-kafka-1 kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic weather_requests \
    --from-beginning
```

## Docker Services

The system uses the following Docker services:

1. **Zookeeper**: Manages Kafka cluster state
2. **Kafka**: Message broker for service communication
3. **ML Model Service**: PySpark-based prediction service
4. **Weather Worker**: Processes weather requests and coordinates with ML service

## Data Flow

1. Client sends request to `weather_requests` topic
2. Weather Worker:
   - Receives request from `weather_requests`
   - Fetches weather data from Open-Meteo API
   - Sends data to `model_requests` topic
3. ML Model Service:
   - Processes data from `model_requests`
   - Sends prediction to `model_results` topic
4. Weather Worker:
   - Receives prediction from `model_results`
   - Sends final result to `weather_results` topic
5. Client receives result from `weather_results` topic

## Troubleshooting

1. If Kafka connection fails, verify the bootstrap server address:
   - Use `localhost:9092` when running services locally
   - Use `kafka:9092` when running in Docker

2. Verify topics exist:
```bash
docker exec predictive_policing_system-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

3. Common Issues:
   - Kafka connection refused: Ensure Kafka container is running
   - Model not found: Check MODEL_PATH environment variable
   - Topic not found: Run the topic creation commands
   - Java not found: Verify Java 11 installation for PySpark

## Development

1. Adding new features:
   - Add new topic names to `.env`
   - Update docker-compose.yml for new services
   - Follow existing message patterns for Kafka communication

2. Testing:
   - Use provided test_weather.py as example
   - Monitor topic messages for debugging
   - Check container logs for service issues
