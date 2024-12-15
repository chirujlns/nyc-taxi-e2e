
# Resolving PostgreSQL COPY Permission Error

When encountering a `Permission denied` error with the `COPY` command in PostgreSQL, you can use the `\copy` command to load data from the client side.

---

## **Problem**
Error when running `COPY`:
```plaintext
ERROR: could not open file "/Users/cmd/Downloads/yellow_taxi_trip/yellow_tripdata_2019-01.csv" for reading: Permission denied
HINT: COPY FROM instructs the PostgreSQL server process to read a file. You may want a client-side facility such as psql's \copy.
```

---

## **Solution: Use `\copy`**

Replace `COPY` with `\copy` in the `psql` terminal. Here’s the corrected command:

```sql
\copy nyc_taxi_trips (VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge)
FROM '/Users/cmd/Downloads/yellow_taxi_trip/yellow_tripdata_2019-01.csv'
DELIMITER ','
CSV HEADER;
```

---

## **Explanation of `\copy`**
- **`\copy`**: Runs on the **client side** (your local machine), unlike `COPY`, which runs on the **server side**.
- The syntax remains the same as the `COPY` command.
- Ensures compatibility with files stored on your local machine.

---

## **Steps to Execute:**
1. Open the `psql` terminal.
2. Connect to your desired database using:
   ```sql
   \c database_name
   ```
3. Execute the `\copy` command provided above.
4. Ensure the file path and permissions are correct.

---

## **Notes**
- The file must exist and be accessible on your local machine.
- If you still face issues:
  - Double-check the file path.
  - Ensure the file has appropriate read permissions:
    ```bash
    chmod 644 /Users/cmd/Downloads/yellow_taxi_trip/yellow_tripdata_2019-01.csv
    ```
  - Verify you are in the correct database.

---

Let me know if you encounter any further issues!
