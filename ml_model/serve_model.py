from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
import os
import logging
import atexit
from pyspark.ml.regression import RandomForestRegressionModel


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize Spark Session
try:
    spark = SparkSession.builder.master("local[1]").appName("ML_API").getOrCreate()
    logger.info("Spark session initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Spark session: {e}")
    raise

# Ensure Spark session stops gracefully when the app shuts down
atexit.register(lambda: spark.stop())

# Load Model
MODEL_PATH = os.getenv("MODEL_PATH", "ml_model/crime_prediction_model")
try:
    model = RandomForestRegressionModel.load(MODEL_PATH)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Validate input data dynamically
        data = request.json
        required_keys = [
            "temperature", "relative_humidity", "rain", "snowfall", "snow_depth",
            "cloud_cover", "wind_speed_10m", "wind_direction_10m",
            "Latitude", "Longitude", "date", "time"
        ]
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_keys)}"}), 400

        # Extract date and time and calculate DAY_OF_YEAR and HOUR
        from datetime import datetime

        try:
            input_date = datetime.strptime(data["date"], "%Y-%m-%d")
            input_time = datetime.strptime(data["time"], "%H:%M")
            day_of_year = input_date.timetuple().tm_yday
            hour = input_time.hour
        except ValueError:
            return jsonify({"error": "Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM' for time."}), 400

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

        # Create DataFrame for model
        input_df = spark.createDataFrame([input_data])

        # Make prediction
        prediction = model.transform(input_df).collect()[0]["prediction"]
        logger.info(f"Prediction made successfully: {prediction}")
        return jsonify({"prediction": prediction})

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "An internal server error occurred. Please try again."}), 500

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001)
    except Exception as e:
        logger.error(f"Error starting Flask server: {e}")
