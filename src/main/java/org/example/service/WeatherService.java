package org.example.service;

@Service
@Slf4j
public class WeatherService {
    private final KafkaTemplate<String, String> kafkaTemplate;

    @KafkaListener(topics = "weather-data", groupId = "weather-group")
    public void consumeWeatherData(String message) {
        WeatherData weatherData = parseWeatherData(message);
        // Process weather data
        log.info("Received weather data: {}", weatherData);
    }

    public void fetchWeatherData() {
        // Implement weather API calls and send to Kafka
        // Use WebClient to call weather API
    }
}