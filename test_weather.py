from weather_service.service import WeatherService


def main():
    weather = WeatherService()
    try:
        result = weather.get_weather(
            latitude=50.87922,
            longitude=-73.86106,
            date="2024-12-17",
            time_str="3:45 PM"
        )

        print(result)


    finally:
        weather.close()



if __name__ == "__main__":
    main()