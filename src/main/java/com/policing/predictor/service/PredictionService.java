package com.policing.predictor.service;

import com.policing.predictor.model.PredictionResult;
import com.policing.predictor.model.WeatherData;
import org.apache.spark.ml.feature.VectorAssembler;
import org.apache.spark.ml.regression.RandomForestRegressor;
import org.apache.spark.ml.regression.RandomForestRegressionModel;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import org.apache.spark.ml.evaluation.RegressionEvaluator;
import java.util.ArrayList;
import java.util.List;

@Service
public class PredictionService {
    private final DataProcessingService dataProcessingService;
    private final WeatherService weatherService;

    public PredictionService(DataProcessingService dataProcessingService, WeatherService weatherService) {
        this.dataProcessingService = dataProcessingService;
        this.weatherService = weatherService;
    }

    public PredictionResult predictCrimeRisk(String location, WeatherData currentWeather) {
        Dataset<Row> historicalData = dataProcessingService.loadHistoricalData();
        Dataset<Row> processedData = dataProcessingService.preprocessData(historicalData);

        // Create features vector
        VectorAssembler assembler = new VectorAssembler()
                .setInputCols(new String[]{"HOUR", "DOW", "temperature", "humidity"})
                .setOutputCol("features");

        // Train model (simplified policing)
        RandomForestRegressor rf = new RandomForestRegressor()
                .setLabelCol("label")
                .setFeaturesCol("features");

        // Make prediction
        // Return result
    }
}