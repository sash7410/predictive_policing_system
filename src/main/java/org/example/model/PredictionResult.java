package org.example.model;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResult {
    private String location;
    private Double riskScore;
    private String timestamp;
    private List<String> contributingFactors;
}