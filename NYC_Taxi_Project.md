
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
1. Configure **AWS DMS** to load data from the source (e.g., local database) to Amazon S3.
2. Organize raw data into folders in the S3 bucket (e.g., `/raw/nyc_taxi/`).
3. Enable incremental loading for updated data using job bookmarks.

### 2. Data Cleaning and Transformation
#### Using AWS Glue:
1. Create Glue Crawlers to catalog raw data.
2. Develop Glue ETL jobs to perform the following tasks:
   - Cleaning: Remove null or irrelevant data.
   - Transformation: Apply business rules, filter columns, and standardize formats.
   - Aggregation: Summarize trip data (e.g., total trips per day, revenue by zone).
3. Save the transformed data in Parquet format to `/processed/nyc_taxi/`.

#### Workflow Automation:
- Set up a Glue Workflow to automate the above steps and trigger it whenever new data is ingested.

### 3. Data Warehousing
#### Using Amazon Redshift:
1. Create an **external schema** to query processed data directly from S3 using Redshift Spectrum.
2. Load processed data into Redshift tables for optimized querying.
3. Configure incremental loading for ongoing updates.

#### Cluster Configuration:
- Use **RA3 nodes** for scalability and cost efficiency.
- Set up appropriate distribution keys and sort keys for performance optimization.

### 4. Analytics and Reporting
1. Use SQL queries in Redshift to perform advanced analytics (e.g., revenue trends, trip patterns).
2. Integrate Redshift with BI tools like Amazon QuickSight for visualization.

## Possible Enhancements
- Implement **data quality checks** using AWS Glue DataBrew.
- Use **AWS Step Functions** to orchestrate the entire workflow.
- Incorporate **event-driven triggers** using S3 events or AWS Lambda.

## Folder Structure
```
/raw/nyc_taxi/
    - trip_data.csv
    - location_data.csv
/processed/nyc_taxi/
    - trip_data_cleaned.parquet
    - location_data_cleaned.parquet
```

## Key Considerations
- Ensure data security and encryption in S3 and Redshift.
- Monitor ETL jobs and workflows for failures using AWS CloudWatch.
- Optimize storage costs by archiving older data in Amazon S3 Glacier.

## Conclusion
This project demonstrates the use of AWS services to build an efficient data pipeline for NYC Taxi data, enabling scalable analytics and reporting.
