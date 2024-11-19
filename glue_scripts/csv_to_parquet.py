import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions

# Initialize Glue context
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session

# Read parameters
args = getResolvedOptions(sys.argv, ["source_path", "destination_path"])
source_path = args["source_path"]
destination_path = args["destination_path"]

try:
    # Read CSV data from the raw folder
    raw_data = spark.read.csv(source_path, header=True, inferSchema=True)

    # Add partitioning logic (e.g., partition by year and month)
    partitioned_data = raw_data.withColumn("year", raw_data["tpep_pickup_datetime"].substr(1, 4)) \
                               .withColumn("month", raw_data["tpep_pickup_datetime"].substr(6, 2))

    # Write data in Parquet format to the processed folder with partitioning
    partitioned_data.write.partitionBy("year", "month").parquet(destination_path, mode="overwrite")

    print("Job completed successfully.")

except Exception as e:
    # Log errors to CloudWatch
    print(f"Error occurred: {str(e)}")
    raise