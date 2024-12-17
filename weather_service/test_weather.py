from service import WeatherService


def main():
    weather = WeatherService()
    try:
        result = weather.get_weather(
            latitude=40.87922,
            longitude=-73.86106,
            date="2024-12-17",
            time_str="3:45 PM"
        )

        print("\nWeather Data:")
        print(f"Temperature: {result['temperature']}°C")
        print(f"Humidity: {result['humidity']}%")
        print(f"Rain: {result['rain']} mm")
        print(f"Snowfall: {result['snowfall']} cm")
        print(f"Snow Depth: {result['snow_depth']} cm")
        print(f"Cloud Cover: {result['cloud_cover']}%")
        print(f"Wind Speed: {result['wind_speed']} km/h")
        print(f"Wind Direction: {result['wind_direction']}°")


    finally:
        weather.close()



if __name__ == "__main__":
    main()