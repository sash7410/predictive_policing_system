from flask import Flask, request, jsonify, send_file
from weather_service.service import WeatherService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def home():
    return send_file('templates/index.html')


@app.route('/get_weather', methods=['POST'])
def get_weather():
    try:
        data = request.json
        logger.info(f"Received request: {data}")

        weather_service = WeatherService()
        try:
            result = weather_service.get_weather(
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                date=data['date'],
                time_str=data['time_str']
            )

            logger.info(f"Got result: {result}")
            return jsonify({
                'success': True,
                'data': result
            })

        finally:
            weather_service.close()

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)