
# PostgreSQL on Mac: Connect, List Databases, and Load CSV Data

## **Step 1: Open Terminal**
Launch the terminal on your Mac.

---

## **Step 2: Switch to the `postgres` User**
Run the following command to switch to the `postgres` user:

```bash
sudo -i -u postgres
```

Alternatively, if PostgreSQL is set up without `sudo`, you can directly run:

```bash
psql -U postgres
```

If a password is required, enter it when prompted.

---

## **Step 3: List All Databases**
Once in the `psql` prompt, use the following command to list all databases:

```sql
\l
```

This will display a list of databases available on your PostgreSQL instance.

---

## **Step 4: Connect to a Specific Database**
To connect to a specific database, use the `\c` command followed by the database name:

```sql
\c database_name
```

Replace `database_name` with the name of the database you want to connect to.

---

## **Step 5: Create a Table for the CSV Data**
Before loading CSV data, ensure the table schema matches the CSV file structure. For example:

```sql
CREATE TABLE example_table (
    id SERIAL PRIMARY KEY,
    name TEXT,
    age INT,
    city TEXT
);
```

Modify the columns and data types to match your CSV file.

---

## **Step 6: Load CSV Data into the Table**
Use the `COPY` command to load CSV data into the table. Ensure the CSV file is accessible to PostgreSQL.

```sql
COPY example_table (id, name, age, city)
FROM '/path/to/your/file.csv'
DELIMITER ','
CSV HEADER;
```

- Replace `/path/to/your/file.csv` with the full path to your CSV file.
- `DELIMITER ','` specifies the delimiter used in the CSV file (`,` for a comma-separated file).
- `CSV HEADER` indicates that the CSV file contains a header row.

---

## **Step 7: Verify the Data**
After loading the data, you can check the table content with:

```sql
SELECT * FROM example_table LIMIT 10;
```

---

## **Step 8: Exit the `psql` Prompt**
To exit `psql`, type:

```sql
\q
```

---

## **Notes**
- Ensure that the PostgreSQL server is running before connecting. You can start it with:
  ```bash
  brew services start postgresql
  ```
- Adjust file permissions so the PostgreSQL server can access the CSV file.

---

Let me know if you encounter any issues or need further clarification!
