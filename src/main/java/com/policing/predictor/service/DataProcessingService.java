package com.policing.predictor.service;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;
import static org.apache.spark.sql.functions.*;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import java.util.Arrays;
import java.util.List;

@Service
@Slf4j
public class DataProcessingService {
    private final SparkSession sparkSession;

    public DataProcessingService(SparkSession sparkSession) {
        this.sparkSession = sparkSession;
    }

    public Dataset<Row> loadHistoricalData() {
        return sparkSession.read()
                .format("csv")
                .option("header", "true")
                .load("path/to/NYPD_Arrests_Data_Historic.csv")
                .select("ARREST_DATE", "PD_DESC", "BOROUGH", "Latitude", "Longitude");
    }

    public Dataset<Row> preprocessData(Dataset<Row> data) {
        // Clean and transform data
        return data.na().drop()
                .withColumn("ARREST_DATE", to_timestamp(col("ARREST_DATE")))
                .withColumn("HOUR", hour(col("ARREST_DATE")))
                .withColumn("DOW", dayofweek(col("ARREST_DATE")));
    }
}