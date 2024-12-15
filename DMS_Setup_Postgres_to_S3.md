
# AWS DMS Setup to Load PostgreSQL Data to S3

This document outlines the detailed steps to set up AWS DMS for migrating PostgreSQL data to S3, including a full load and incremental updates using Change Data Capture (CDC).

---

## Step 1: Prerequisites
Before configuring AWS DMS:
1. Ensure your PostgreSQL database is accessible from AWS DMS:
   - Verify the database instance is in a publicly accessible network or is accessible within your VPC.
   - Ensure required ports (default: 5432) are open.
   - Security groups must allow DMS access.

2. **IAM Role for DMS**:
   - Create an IAM role for DMS with the following policies:
     - `AmazonS3FullAccess` (for S3 target access).
     - `AWSGlueConsoleFullAccess` (if you're cataloging the data).
     - `AWSDatabaseMigrationServiceRole`.

---

## Step 2: Configure an S3 Bucket
1. Create an S3 bucket to store the migrated data. Example:
   ```
   Bucket Name: nyc-taxi-dms-target
   Folder: /full_load/
   ```

2. Set appropriate permissions for DMS to write to the bucket:
   - Attach a bucket policy:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Principal": {
             "Service": "dms.amazonaws.com"
           },
           "Action": "s3:PutObject",
           "Resource": "arn:aws:s3:::nyc-taxi-dms-target/*"
         }
       ]
     }
     ```

---

## Step 3: Configure DMS Source Endpoint
1. Go to **AWS DMS Console** > Click **Endpoints** > **Create Endpoint**:
   - **Endpoint Type**: Source.
   - **Engine**: PostgreSQL.
   - **Endpoint Identifier**: `pg_source_endpoint`.
   - **Server Name**: Your PostgreSQL server's hostname or IP.
   - **Port**: 5432 (default).
   - **SSL Mode**: `require` (if applicable).
   - **Username** and **Password**: Credentials for the PostgreSQL database.
2. Test the connection to ensure DMS can connect.

---

## Step 4: Configure DMS Target Endpoint
1. Click **Create Endpoint** again:
   - **Endpoint Type**: Target.
   - **Engine**: Amazon S3.
   - **Endpoint Identifier**: `s3_target_endpoint`.
   - **Bucket Name**: `nyc-taxi-dms-target`.
   - **IAM Role ARN**: The IAM role you created.
   - **S3 Folder**: `/full_load/`.

2. Test the connection to verify access.

---

## Step 5: Create a DMS Replication Task
1. Go to **Database Migration Tasks** > **Create Task**:
   - **Task Identifier**: `pg_to_s3_task`.
   - **Replication Instance**: Choose a replication instance.
   - **Source Endpoint**: `pg_source_endpoint`.
   - **Target Endpoint**: `s3_target_endpoint`.
   - **Migration Type**: Full Load.
2. Configure **Table Mappings**:
   - Include the table(s) from your PostgreSQL database. Example:
     ```json
     {
       "rules": [
         {
           "rule-type": "selection",
           "rule-id": "1",
           "rule-name": "include-table",
           "object-locator": {
             "schema-name": "public",
             "table-name": "nyc_taxi_trips"
           },
           "rule-action": "include"
         }
       ]
     }
     ```

3. **Advanced Settings**:
   - **Enable Partitioning**: Split large tables into smaller files.
   - **S3 Output Format**: Select `CSV` or `JSON` (based on your requirements).
     - Example for CSV:
       ```
       Include LOBs: Disable
       Max File Size: 1GB
       ```

4. Start the task to perform the full load.

---

## Step 6: Verify the Data in S3
1. Navigate to the S3 bucket (`nyc-taxi-dms-target/full_load/`) in the AWS Console.
2. Verify the data files (e.g., `nyc_taxi_trips_part1.csv`, `nyc_taxi_trips_part2.csv`).

---

## Step 7: Configure Incremental Updates with CDC
1. Modify the replication task:
   - Enable **CDC (Change Data Capture)** in the task settings.
   - Ensure WAL (Write-Ahead Logging) is enabled in your PostgreSQL database:
     ```sql
     ALTER SYSTEM SET wal_level = logical;
     ALTER SYSTEM SET max_replication_slots = 5;
     ALTER SYSTEM SET max_wal_senders = 5;
     ```
     Restart the PostgreSQL instance for changes to take effect.
   - Grant replication permissions to the DMS user:
     ```sql
     GRANT rds_replication TO <your_user>;
     ```

2. Run the task again to capture changes.

---

### Summary of Steps
1. **Setup DMS Source Endpoint**: PostgreSQL database.
2. **Setup DMS Target Endpoint**: Amazon S3 bucket.
3. **Run Full Load Task**: Migrate the initial data to S3.
4. **Enable CDC**: Incrementally capture changes for subsequent months.

This step-by-step process will help you configure DMS to migrate and load your data into S3 effectively.
