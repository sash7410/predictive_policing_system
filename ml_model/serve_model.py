from pyspark.sql import SparkSession
import os
import logging
from pyspark.ml.regression import RandomForestRegressionModel
from pyspark.sql.functions import sin, cos, col
from pyspark.ml.feature import VectorAssembler, StandardScaler
from kafka import KafkaConsumer, KafkaProducer
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelServer:
    def __init__(self, kafka_server='localhost:9092'):
        # Initialize Spark Session
        self.spark = SparkSession.builder.master("local[1]").appName("ML_API").getOrCreate()
        logger.info("Spark session initialized successfully.")

        # Load Model
        MODEL_PATH = os.getenv("MODEL_PATH", "ml_model/crime_prediction_model")
        self.model = RandomForestRegressionModel.load(MODEL_PATH)
        logger.info("Model loaded successfully.")

        # Initialize Kafka
        self.consumer = KafkaConsumer(
            'model_requests',
            bootstrap_servers=[kafka_server],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='model_server'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def process_data(self, data):
        try:
            # Extract date and time and calculate DAY_OF_YEAR and HOUR
            from datetime import datetime
            input_date = datetime.strptime(data["date"], "%Y-%m-%d")
            input_time = datetime.strptime(data["time"], "%H:%M")
            day_of_year = input_date.timetuple().tm_yday
            hour = input_time.hour

            # Prepare input for model
            input_data = {
                "temperature": float(data["temperature"]),
                "relative_humidity": float(data["relative_humidity"]),
                "rain": float(data["rain"]),
                "snowfall": float(data["snowfall"]),
                "snow_depth": float(data["snow_depth"]),
                "cloud_cover": float(data["cloud_cover"]),
                "wind_speed_10m": float(data["wind_speed_10m"]),
                "wind_direction_10m": float(data["wind_direction_10m"]),
                "Latitude": float(data["Latitude"]),
                "Longitude": float(data["Longitude"]),
                "DAY_OF_YEAR": int(day_of_year),
                "HOUR": int(hour),
            }

            features = [
                "sin_day", "cos_day", "sin_hour", "cos_hour",
                "temperature", "relative_humidity", "rain",
                "snowfall", "snow_depth", "cloud_cover", "wind_speed_10m", "wind_direction_10m",
                "Latitude", "Longitude"
            ]

            # Create DataFrame for model
            input_df = self.spark.createDataFrame([input_data])
            input_df = input_df.withColumn("sin_day", sin(2 * 3.14159 * col("DAY_OF_YEAR") / 366))
            input_df = input_df.withColumn("cos_day", cos(2 * 3.14159 * col("DAY_OF_YEAR") / 366))
            input_df = input_df.withColumn("sin_hour", sin(2 * 3.14159 * col("HOUR") / 24))
            input_df = input_df.withColumn("cos_hour", cos(2 * 3.14159 * col("HOUR") / 24))

            assembler = VectorAssembler(inputCols=features, outputCol="features")
            scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=True)

            input_df = assembler.transform(input_df)
            input_df = scaler.fit(input_df).transform(input_df)

            # Make prediction
            prediction = self.model.transform(input_df).collect()[0]["prediction"]
            return {"prediction": prediction}

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {"error": str(e)}

    def start(self):
        logger.info("Model server started...")
        try:
            for message in self.consumer:
                data = message.value
                request_id = data.get('request_id')

                # Process the request and get prediction
                result = self.process_data(data)
                result['request_id'] = request_id

                # Send back the result
                self.producer.send('model_results', result)
                self.producer.flush()
                logger.info(f"Sent prediction: {result}")

        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.close()

    def close(self):
        self.consumer.close()
        self.producer.close()
        self.spark.stop()
        logger.info("Model server shut down.")


if __name__ == "__main__":
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"Connecting to Kafka at: {kafka_server}")  # Debug print
    server = ModelServer()
    server.start()