
# NYC Taxi Data End-to-End Project

## Overview
This project involves handling NYC Taxi data consisting of **trip data** and **location data** stored in CSV files. The workflow covers end-to-end data engineering, starting from ingestion, cleaning, transformation, and finally, storing it in a data warehouse using AWS services.

## Objectives
1. Ingest data from various sources into a data lake.
2. Perform data cleaning and transformation using AWS Glue.
3. Store processed data in a data warehouse (AWS Redshift) for analytics and reporting.

## Tools and Services
- **AWS DMS**: For data migration from source systems to the data lake.
- **AWS Glue**: For creating crawlers, ETL jobs, and workflows.
- **Amazon S3**: For storing raw and processed data.
- **Amazon Redshift**: For data warehousing and querying.
- **JDBC Connections**: To connect with external databases.
- **Parquet Format**: For efficient storage and querying.

## Scenarios and Steps

### 1. Data Ingestion
#### Sources:
- NYC Taxi Trip Data (CSV files)
- NYC Taxi Location Data (CSV files)

#### Steps:
1. **AWS DMS Setup**:
   - Create a source endpoint (e.g., a PostgreSQL database or on-premise database where raw data resides).
   - Create a target endpoint for **Amazon S3**.
   - Define a migration task in AWS DMS:
     - Set task type to **Full Load and CDC (Change Data Capture)** for incremental updates.
     - Configure task settings to handle schema mapping and data transformations.
   - Test endpoints and start the migration task.

2. **Organize Raw Data in S3**:
   - Create an S3 bucket, e.g., `nyc-taxi-data`.
   - Define a folder structure:
     ```
     /raw/nyc_taxi/
         - trip_data.csv
         - location_data.csv
     ```
   - Use S3 lifecycle policies to transition older raw data to S3 Glacier for cost savings.

3. **Incremental Loading**:
   - Use **AWS DMS job bookmarks** to track and process only new or updated data.
   - Configure CDC settings to capture changes (INSERT, UPDATE, DELETE).

### 2. Data Cleaning and Transformation
#### Using AWS Glue:
1. **Create Glue Crawlers**:
   - Go to **AWS Glue Console** > Crawlers.
   - Create a new crawler to scan the `/raw/nyc_taxi/` folder.
   - Specify the data source as S3 and output the catalog to the AWS Glue Data Catalog.
   - Run the crawler to generate the schema.

2. **Develop Glue ETL Jobs**:
   - Write a Glue ETL job in **Python (PySpark)**:
     ```python
     import pyspark.sql.functions as F
     from awsglue.context import GlueContext
     from pyspark.context import SparkContext

     glueContext = GlueContext(SparkContext.getOrCreate())
     spark = glueContext.spark_session

     # Load raw data
     trip_data = spark.read.csv("s3://nyc-taxi-data/raw/nyc_taxi/trip_data.csv", header=True)
     location_data = spark.read.csv("s3://nyc-taxi-data/raw/nyc_taxi/location_data.csv", header=True)

     # Clean data: Remove null values
     trip_data_cleaned = trip_data.na.drop()
     location_data_cleaned = location_data.na.drop()

     # Transform data: Standardize date formats
     trip_data_cleaned = trip_data_cleaned.withColumn("pickup_datetime", F.to_timestamp("pickup_datetime"))

     # Write to processed folder in Parquet format
     trip_data_cleaned.write.parquet("s3://nyc-taxi-data/processed/trip_data_cleaned.parquet", mode="overwrite")
     location_data_cleaned.write.parquet("s3://nyc-taxi-data/processed/location_data_cleaned.parquet", mode="overwrite")
     ```

3. **Workflow Automation**:
   - Create a **Glue Workflow**:
     - Add crawlers as the first step to catalog data.
     - Add the Glue ETL job as the second step.
     - Set triggers for the workflow (e.g., on file upload to S3).

### 3. Data Warehousing
#### Using Amazon Redshift:
1. **Redshift Cluster Setup**:
   - Launch an **Amazon Redshift RA3 node** cluster with appropriate node types and sizes.
   - Configure the **VPC** for network access.
   - Create required schemas and tables using SQL:
     ```sql
     CREATE TABLE trip_data (
         trip_id INT,
         pickup_datetime TIMESTAMP,
         dropoff_datetime TIMESTAMP,
         passenger_count INT,
         trip_distance FLOAT,
         fare_amount FLOAT
     );

     CREATE TABLE location_data (
         location_id INT,
         borough VARCHAR,
         zone VARCHAR,
         service_zone VARCHAR
     );
     ```

2. **External Schema for Spectrum**:
   - Create an external schema in Redshift linked to the S3 bucket:
     ```sql
     CREATE EXTERNAL SCHEMA nyc_taxi
     FROM DATA CATALOG
     DATABASE 'nyc_taxi_db'
     IAM_ROLE 'arn:aws:iam::your-account-id:role/RedshiftSpectrumRole';
     ```

3. **Load Data to Redshift**:
   - Use **COPY Command** for efficient loading:
     ```sql
     COPY trip_data
     FROM 's3://nyc-taxi-data/processed/trip_data_cleaned.parquet'
     IAM_ROLE 'arn:aws:iam::your-account-id:role/RedshiftRole'
     FORMAT AS PARQUET;
     ```

4. **Incremental Updates**:
   - Schedule Glue ETL jobs to append new data to Redshift periodically.

### 4. Analytics and Reporting
#### Technical Implementation
1. **Querying Data**:
   - Run SQL queries in Redshift to analyze trends, e.g.:
     ```sql
     SELECT borough, COUNT(*) AS trip_count
     FROM location_data l
     JOIN trip_data t
     ON l.location_id = t.trip_id
     GROUP BY borough
     ORDER BY trip_count DESC;
     ```

2. **Visualization in QuickSight**:
   - Connect QuickSight to Redshift.
   - Create dashboards showing:
     - Trip count trends by borough.
     - Revenue patterns over time.

### Enhancements
#### Technical Implementation
1. **Data Quality Checks with DataBrew**:
   - Create a **DataBrew Project** to profile data and identify issues.
   - Apply transformations to fix data anomalies.

2. **Orchestration with Step Functions**:
   - Create a Step Function workflow:
     - Trigger on S3 events for new file uploads.
     - Invoke Glue jobs, crawlers, and Redshift queries.

3. **Event-Driven Triggers with Lambda**:
   - Write a Lambda function triggered by S3 file upload events:
     ```python
     import boto3

     def lambda_handler(event, context):
         glue = boto3.client('glue')
         response = glue.start_workflow_run(Name='nyc_taxi_workflow')
     ```

### Folder Structure
```
/raw/nyc_taxi/
    - trip_data.csv
    - location_data.csv
/processed/nyc_taxi/
    - trip_data_cleaned.parquet
    - location_data_cleaned.parquet
```

---
