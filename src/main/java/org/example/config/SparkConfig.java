package org.example.config;

@Configuration
public class SparkConfig {
    @Value("${spark.app.name}")
    private String appName;

    @Bean
    public SparkSession sparkSession() {
        return SparkSession
                .builder()
                .appName(appName)
                .master("local[*]")
                .getOrCreate();
    }
}