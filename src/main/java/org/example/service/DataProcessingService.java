package org.example.service;

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