import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
import logging
from pyspark.sql.functions import col, year, month

# Suppress Spark's excessive logging (including Log4j warnings)
sc = SparkContext.getOrCreate()
logger = sc._jvm.org.apache.log4j
logger.LogManager.getLogger("org").setLevel(logger.Level.ERROR)
logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)

# Initialize Glue context
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Set up a Python logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Read parameters
args = getResolvedOptions(sys.argv, ["source_path", "destination_path"])
source_path = args["source_path"]
destination_path = args["destination_path"]

try:
    log.info("Starting the job...")

    # Read CSV data from the raw folder
    raw_data = spark.read.csv(source_path, header=True, inferSchema=True)

    # Apply recipe logic
    # Extract year and month from tpep_pickup_datetime
    data_with_year_month = raw_data.withColumn("year", year(col("tpep_pickup_datetime"))) \
                                   .withColumn("month", month(col("tpep_pickup_datetime")))

    # Filter out rows where year is not 2019
    filtered_data = data_with_year_month.filter(col("year") == 2019)

    # # Filter out rows where month is not January (1)
    # filtered_data = filtered_data.filter(col("month") == 1)

    # Write data in Parquet format to the processed folder with partitioning
    filtered_data.write.partitionBy("year", "month").parquet(destination_path, mode="overwrite")

    log.info(f"Job completed successfully. Data written to {destination_path}")

except Exception as e:
    log.error(f"Error occurred during job execution: {str(e)}")
    raise