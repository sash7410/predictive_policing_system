import os
from serve_model import ModelServer

if __name__ == "__main__":
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    server = ModelServer(kafka_server=kafka_server)
    server.start()