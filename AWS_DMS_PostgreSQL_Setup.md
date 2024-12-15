
# Setting Up AWS DMS with Self-Hosted PostgreSQL on Mac

## Step 1: Configure PostgreSQL for Remote Access

### 1. Edit `postgresql.conf` to Allow External Connections:
- Locate the PostgreSQL configuration file on your Mac. It’s usually found at `/usr/local/var/postgres/postgresql.conf`.
- Open the file using a text editor:
  ```bash
  nano /usr/local/var/postgres/postgresql.conf
  ```
- Look for the line:
  ```
  #listen_addresses = 'localhost'
  ```
- Uncomment it and set it to accept connections from all addresses:
  ```
  listen_addresses = '*'
  ```
- Save and close the file.

### 2. Edit `pg_hba.conf` to Allow Host-Based Authentication:
- Locate the `pg_hba.conf` file. It’s usually in the same directory as `postgresql.conf`.
- Add the following line to allow connections from the AWS DMS replication instance’s IP or range:
  ```
  host    all    all    0.0.0.0/0    md5
  ```
  > **Note:** Replace `0.0.0.0/0` with the IP range of your AWS DMS replication instance for better security.
- Save and close the file.

### 3. Restart PostgreSQL Service:
- Apply the changes by restarting the PostgreSQL server:
  ```bash
  brew services restart postgresql
  ```

---

## Step 2: Open Firewall Ports on Your Mac

### 1. Check Firewall Status:
- Ensure the firewall on your Mac allows connections to PostgreSQL (port 5432).
- To check the firewall status:
  ```bash
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
  ```

### 2. Allow Incoming Connections on Port 5432:
- Use the following command to open port 5432:
  ```bash
  sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
  ```
- Alternatively, configure your firewall using **System Preferences**:
  - Go to **System Preferences > Security & Privacy > Firewall**.
  - Add PostgreSQL to the list of allowed apps.

---

## Step 3: Verify Database Accessibility

### 1. Test Local Connectivity:
- Ensure PostgreSQL is running and accessible locally:
  ```bash
  psql -h localhost -U <username> -p 5432 -d <database_name>
  ```

### 2. Test Remote Connectivity:
- From an external system (or an EC2 instance in AWS):
  ```bash
  psql -h <your-mac-public-ip> -U <username> -p 5432 -d <database_name>
  ```
- If this fails, double-check your network and firewall configurations.

---

## Step 4: Set Up AWS DMS Replication Instance

### 1. Create a DMS Replication Instance in AWS:
- Ensure it’s in a public subnet if your Mac's database is exposed over the internet, or configure VPN/Direct Connect if using a private subnet.
- Attach a security group that allows outbound connections to your Mac’s public IP on port 5432.

### 2. Create a Source Endpoint in DMS:
- Configure the source endpoint with your Mac’s public IP and database credentials.

### 3. Test the Connection:
- In the DMS Console, test the connection to your source endpoint. This step ensures that the AWS DMS instance can reach your PostgreSQL database.

---

## Step 5: Secure the Configuration

### 1. Restrict Firewall Rules:
- Once verified, replace `0.0.0.0/0` in `pg_hba.conf` and firewall rules with the IP or CIDR range of the DMS instance.

### 2. Use SSL for Secure Communication:
- Configure PostgreSQL to use SSL for encrypted connections:
  - Generate SSL certificates.
  - Update `postgresql.conf` to point to the certificate files.

---

## Summary

This guide ensures that your self-hosted PostgreSQL database on Mac is accessible to AWS DMS for data migration while maintaining security and connectivity. Follow the steps sequentially for a smooth setup.
