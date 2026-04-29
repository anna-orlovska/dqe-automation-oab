# Real Framework Setup - Step by Step

This is a **real** plan for running the framework. Not theoretical, but practical.

## Phase 1: Infrastructure Setup (30 minutes)

### Step 1: Start Docker Containers
```bash
cd /path/to/DQE_Framework
docker-compose up -d

# Verify
docker ps
# Should see: postgres and jenkins
```

### Step 2: Initialize PostgreSQL Database
```bash
# Wait 10 seconds for PostgreSQL to start
sleep 10

# Create table using psql
psql -h localhost -p 5434 -U myuser -d mydatabase << 'EOF'

CREATE TABLE IF NOT EXISTS patient_treatment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    treatment_cost DECIMAL(10, 2) NOT NULL,
    facility_type VARCHAR(50),
    visit_date DATE NOT NULL,
    time_spent INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO patient_treatment (patient_id, treatment_cost, facility_type, visit_date, time_spent)
VALUES
    (1, 150.00, 'Hospital', '2024-01-01', 120),
    (1, 100.00, 'Clinic', '2024-01-05', 45),
    (2, 200.00, 'Hospital', '2024-01-02', 180),
    (2, 75.00, 'Clinic', '2024-01-10', 30),
    (3, 125.00, 'Hospital', '2024-01-03', 90),
    (3, 50.00, 'Clinic', '2024-01-15', 20),
    (4, 300.00, 'Hospital', '2024-01-04', 240),
    (4, 100.00, 'Clinic', '2024-01-12', 40),
    (5, 175.00, 'Hospital', '2024-01-08', 150),
    (5, 80.00, 'Clinic', '2024-01-20', 35);

-- Create aggregated tables for tests
CREATE TABLE IF NOT EXISTS patient_sum_treatment_cost_per_facility_type (
    patient_id INTEGER NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    visit_count INTEGER,
    PRIMARY KEY (patient_id, facility_type)
);

INSERT INTO patient_sum_treatment_cost_per_facility_type (patient_id, facility_type, total_cost, visit_count)
SELECT patient_id, facility_type, SUM(treatment_cost), COUNT(*)
FROM patient_treatment
GROUP BY patient_id, facility_type;

EOF

# Verify
psql -h localhost -p 5434 -U myuser -d mydatabase -c "SELECT COUNT(*) FROM patient_treatment;"
# Should show: 10
```

### Step 3: Create Parquet Data Files
```bash
# Python script to generate Parquet files
python3 << 'EOF'
import pandas as pd
import os

# Create directories
os.makedirs("parquet_data/patient_sum_treatment_cost_per_facility_type", exist_ok=True)
os.makedirs("parquet_data/facility_name_min_time_spent_per_visit_date", exist_ok=True)
os.makedirs("parquet_data/facility_type_avg_time_spent_per_visit_date", exist_ok=True)

# Sample data matching database
data1 = {
    'patient_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
    'facility_type': ['Hospital', 'Clinic', 'Hospital', 'Clinic', 'Hospital', 'Clinic', 'Hospital', 'Clinic', 'Hospital', 'Clinic'],
    'total_cost': [150.00, 100.00, 200.00, 75.00, 125.00, 50.00, 300.00, 100.00, 175.00, 80.00],
    'visit_count': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
}

# Create Parquet files
df = pd.DataFrame(data1)
df.to_parquet("parquet_data/patient_sum_treatment_cost_per_facility_type/data.parquet")

# Create other sample files
df2 = pd.DataFrame({
    'facility_name': ['Hospital', 'Clinic', 'Hospital', 'Clinic'],
    'visit_date': ['2024-01-01', '2024-01-05', '2024-01-02', '2024-01-10'],
    'min_time_spent': [120, 45, 180, 30]
})
df2.to_parquet("parquet_data/facility_name_min_time_spent_per_visit_date/data.parquet")

df3 = pd.DataFrame({
    'facility_type': ['Hospital', 'Clinic', 'Hospital', 'Clinic'],
    'visit_date': ['2024-01-01', '2024-01-05', '2024-01-02', '2024-01-10'],
    'avg_time_spent': [150.0, 37.5, 180.0, 30.0]
})
df3.to_parquet("parquet_data/facility_type_avg_time_spent_per_visit_date/data.parquet")

print("✅ Parquet files created successfully")
EOF
```

## Phase 2: Environment Setup (10 minutes)

### Step 4: Create Virtual Environment
```bash
# Windows
python -m venv venv_3.13
venv_3.13\Scripts\activate

# Linux/macOS
python3 -m venv venv_3.13
source venv_3.13/bin/activate
```

### Step 5: Install Dependencies
```bash
cd "PyTest DQ Framework"
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "pytest|pandas|psycopg2"
```

### Step 6: Create Output Directory
```bash
mkdir -p html_report
mkdir -p allure-results
```

## Phase 3: Run Tests (5-10 minutes)

### Step 7: First Test - Single Smoke Test
```bash
cd "PyTest DQ Framework"

pytest tests/dq\ checks/parquet_files/test_smoke_basic_structure.py::TestDatabaseConnectivity::test_database_connection_established \
  --db_host=localhost \
  --db_port=5434 \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  -v

# Expected: 1 passed
```

### Step 8: Run All Smoke Tests
```bash
pytest tests -m smoke \
  --db_host=localhost \
  --db_port=5434 \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  -v

# Expected: 14 passed
```

### Step 9: Run All Tests
```bash
pytest tests \
  --db_host=localhost \
  --db_port=5434 \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  -v

# Expected: ~70 passed
```

### Step 10: Generate Reports
```bash
pytest tests \
  --db_host=localhost \
  --db_port=5434 \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  --html=../html_report/report.html \
  --self-contained-html \
  --alluredir=../allure-results \
  -v
```

### Step 11: View Reports
```bash
# HTML Report
open html_report/report.html  # macOS
xdg-open html_report/report.html  # Linux
start html_report/report.html  # Windows

# Allure Report (requires allure-commandline)
allure serve allure-results
```

## Phase 4: Jenkins Setup (Optional, 20 minutes)

### Step 12: Access Jenkins
```
URL: http://localhost:8080
```

### Step 13: Get Initial Password
```bash
docker logs jenkins | grep -A 5 "initialAdminPassword"
# or
cat jenkins_home/secrets/initialAdminPassword
```

### Step 14: Create Pipeline Job
1. Click "New Item"
2. Name: "DQ_Tests_Pipeline"
3. Type: "Pipeline"
4. Under Pipeline section:
   - Select "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: Your GitHub repo URL
   - Script Path: PyTest DQ Framework/Jenkinsfile
5. Click "Save"
6. Click "Build Now"

### Step 15: Create Credentials
1. Go to "Manage Jenkins" → "Manage Credentials"
2. Click "Global" → "Add Credentials"
3. Fill in:
   - Kind: Username with password
   - Username: myuser
   - Password: mypassword
   - ID: POSTGRES_SECRET
4. Click "Create"

## Troubleshooting

### Problem: "Connection refused to PostgreSQL"
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs postgres

# Test connection
psql -h localhost -p 5434 -U myuser -d mydatabase -c "SELECT 1"
```

### Problem: "No such file or directory: parquet_data/..."
```bash
# Create directories
mkdir -p parquet_data/patient_sum_treatment_cost_per_facility_type
mkdir -p parquet_data/facility_name_min_time_spent_per_visit_date
mkdir -p parquet_data/facility_type_avg_time_spent_per_visit_date

# Create sample files with Python
# See Step 3 above
```

### Problem: "table patient_treatment does not exist"
```bash
# Create tables
psql -h localhost -p 5434 -U myuser -d mydatabase << 'EOF'
CREATE TABLE patient_treatment (...);
# See Step 2 above
EOF
```

### Problem: "html_report directory not found"
```bash
cd "PyTest DQ Framework"
mkdir -p html_report
```

## Quick Command Cheat Sheet

```bash
# Full automated setup (if you have Python and Docker)
docker-compose up -d
sleep 10
./setup-dev.sh
cd "PyTest DQ Framework"
pytest tests --db_host=localhost --db_port=5434 --db_user=myuser --db_password=mypassword --db_name=mydatabase

# Run specific test type
pytest tests -m smoke ...
pytest tests -m completeness ...
pytest tests -m quality ...

# Generate reports
pytest tests ... --html=../html_report/report.html --self-contained-html --alluredir=../allure-results

# View reports
open html_report/report.html
allure serve allure-results

# Stop Docker
docker-compose down
```

## Success Criteria

✅ All steps completed without errors
✅ 10+ rows in patient_treatment table
✅ 3 Parquet files created successfully
✅ 70+ tests pass
✅ HTML report generated
✅ Allure results generated
✅ Jenkins job can be triggered

## Total Time Required
- Infrastructure: 30 min
- Setup: 10 min
- First test run: 5 min
- **Total: ~45 minutes**
