package com.policing.predictor.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;
import java.util.List;


@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResult {
    private String location;
    private Double riskScore;
    private String timestamp;
    private List<String> contributingFactors;
}