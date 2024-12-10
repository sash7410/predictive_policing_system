package com.policing.predictor.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;
@Data
@NoArgsConstructor
@AllArgsConstructor
public class WeatherData {
    private String timestamp;
    private Double temperature;
    private Double humidity;
    private String weatherCondition;
    private String location;
}