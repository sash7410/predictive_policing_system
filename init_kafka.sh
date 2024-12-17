#!/bin/bash
echo "Waiting for Kafka to be ready..."
sleep 10

docker exec predictive_policing_system-kafka-1 kafka-topics \
    --create --if-not-exists \
    --topic weather_requests \
    --bootstrap-server localhost:9092

docker exec predictive_policing_system-kafka-1 kafka-topics \
    --create --if-not-exists \
    --topic weather_results \
    --bootstrap-server localhost:9092

docker exec predictive_policing_system-kafka-1 kafka-topics \
    --create --if-not-exists \
    --topic model_requests \
    --bootstrap-server localhost:9092

docker exec predictive_policing_system-kafka-1 kafka-topics \
    --create --if-not-exists \
    --topic model_results \
    --bootstrap-server localhost:9092