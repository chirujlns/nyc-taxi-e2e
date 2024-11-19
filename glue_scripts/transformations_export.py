import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import col
from pyspark.sql import DataFrame

# Initialize GlueContext
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
logger = glueContext.get_logger()

# Parameters
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
bucket_name = "nyc-taxi-e2e"
raw_folder = f"s3://{bucket_name}/raw/"
processed_folder = f"s3://{bucket_name}/processed/"
location_csv_path = f"{raw_folder}/taxi+_zone_lookup.csv"

# Load NYC taxi data (e.g., tripdata)
taxi_df = glueContext.create_dynamic_frame.from_catalog(
    database="nyc_taxi_db", table_name="tripdata"
).toDF()

# Load location data
location_df = spark.read.csv(location_csv_path, header=True)

# Perform join on common key (e.g., location_id)
result_df = taxi_df.join(location_df, taxi_df["location_id"] == location_df["location_id"])

# Additional transformations (example: filtering by year)
result_df = result_df.filter(col("trip_year") == 2019)

# Write the result to the processed folder in Parquet format
output_path = f"{processed_folder}/processed_data/"
result_df.write.mode("overwrite").parquet(output_path)

logger.info(f"ETL job completed successfully. Output written to {output_path}")