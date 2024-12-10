package org.example.model;

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