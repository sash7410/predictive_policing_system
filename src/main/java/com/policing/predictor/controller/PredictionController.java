package com.policing.predictor.controller;

import com.policing.predictor.model.PredictionResult;
import com.policing.predictor.service.PredictionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import java.util.List;

@RestController
@RequestMapping("/api/predictions")
@RequiredArgsConstructor
public class PredictionController {
    private final PredictionService predictionService;

    @GetMapping("/{location}")
    public ResponseEntity<PredictionResult> getPrediction(@PathVariable String location) {
        return ResponseEntity.ok(predictionService.predictCrimeRisk(location));
    }
}