package com.policing.predictor.service;

import com.policing.predictor.model.WeatherData;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import reactor.core.publisher.Mono;
import java.time.LocalDateTime;
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