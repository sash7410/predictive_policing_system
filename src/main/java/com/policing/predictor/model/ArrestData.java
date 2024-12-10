package com.policing.predictor.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ArrestData {
    private String arrestDate;
    private String pdDesc;
    private String borough;
    private String latitude;
    private String longitude;
    private String age;
    private String gender;
    private String race;
}