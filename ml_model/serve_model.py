# serve_model.py
from flask import Flask, request, jsonify
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession

app = Flask(__name__)
spark = SparkSession.builder.master("local[*]").appName("ML_API").getOrCreate()
model = PipelineModel.load("crime_prediction_model")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        input_df = spark.createDataFrame([{
            "Latitude": float(data["latitude"]),
            "Longitude": float(data["longitude"]),
            "DAY_OF_YEAR": int(data["DAY_OF_YEAR"]),
            "HOUR": int(data["HOUR"]),
            "temperature": float(data["temperature"]),
            "relative_humidity": float(data["relative_humidity"]),
            "rain": float(data.get("rain", 0)),
            "wind_speed_10m": float(data.get("wind_speed_10m", 0)),
            "wind_direction_10m": float(data.get("wind_direction_10m", 0))
        }])
        prediction = model.transform(input_df).collect()[0]["prediction"]
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
