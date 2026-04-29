# Quick Start Guide

Get up and running with PyTest DQ Framework in minutes.

## Prerequisites

- Python 3.9+
- Docker & Docker Compose (or Podman & Podman Compose)
- Git

## 1. Initial Setup (First Time Only)

### Windows
```bash
setup-dev.bat
```

### Linux/macOS
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

## 2. Activate Virtual Environment

### Windows
```bash
venv_3.13\Scripts\activate
```

### Linux/macOS
```bash
source venv_3.13/bin/activate
```

## 3. Start Database Container

```bash
# Start PostgreSQL and Jenkins containers
docker-compose up -d

# Verify containers are running
docker ps

# Check container logs if needed
docker logs postgres
docker logs jenkins
```

## 4. Run Tests

### All Tests
```bash
cd "PyTest DQ Framework"
pytest tests \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Smoke Tests Only
```bash
cd "PyTest DQ Framework"
pytest tests -m smoke \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Completeness Tests Only
```bash
cd "PyTest DQ Framework"
pytest tests -m completeness \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Quality Tests Only
```bash
cd "PyTest DQ Framework"
pytest tests -m quality \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Specific Test File
```bash
cd "PyTest DQ Framework"
pytest tests/dq\ checks/parquet_files/test_smoke_basic_structure.py \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Specific Test Function
```bash
cd "PyTest DQ Framework"
pytest tests/dq\ checks/parquet_files/test_smoke_basic_structure.py::TestDatabaseConnectivity::test_database_connection_established \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

## 5. Generate Reports

### HTML Report
```bash
cd "PyTest DQ Framework"
pytest tests \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  --html=../html_report/report.html \
  --self-contained-html
```

Then open `html_report/report.html` in your browser.

### Allure Report
```bash
cd "PyTest DQ Framework"
pytest tests \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  --alluredir=../allure-results

# View report (requires allure-commandline)
allure serve allure-results
```

## 6. Stop Containers

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 7. Deactivate Virtual Environment

```bash
deactivate
```

## Common Tasks

### View Test Output with Details
```bash
pytest tests -v -s --tb=long \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Run Tests with Custom Timeout
```bash
pytest tests \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  --timeout=300
```

### Stop on First Failure
```bash
pytest tests -x \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Show Print Statements
```bash
pytest tests -s \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Run Tests in Parallel (requires pytest-xdist)
```bash
pytest tests -n auto \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

### Count Tests Without Running
```bash
pytest tests --collect-only \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase | grep "test session starts" -A 5
```

## Database Access

### Connect from Local Machine
```bash
psql -h localhost -p 5434 -U myuser -d mydatabase
```

### Connect from Docker Container
```bash
docker exec -it postgres psql -U myuser -d mydatabase
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Delete and recreate venv
rm -rf venv_3.13
python3 -m venv venv_3.13
source venv_3.13/bin/activate  # Linux/macOS
# or venv_3.13\Scripts\activate  # Windows
pip install -r "PyTest DQ Framework/requirements.txt"
```

### Container Issues
```bash
# View container logs
docker logs postgres
docker logs jenkins

# Restart containers
docker-compose restart

# Remove and recreate containers
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues
```bash
# Test connection
psql -h localhost -p 5434 -U myuser -d mydatabase -c "SELECT 1"

# Check if container is running
docker ps | grep postgres
```

### Port Already in Use
```bash
# Find process using port 5434
netstat -ano | findstr :5434  # Windows
lsof -i :5434  # Linux/macOS

# If needed, modify docker-compose.yml port mapping:
# Change "5434:5432" to "5435:5432" and use --db_host=localhost --db_port=5435
```

## Environment Variables

Create `.env` file in project root (copy from `.env.example`):
```bash
DB_HOST=localhost
DB_PORT=5434
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
```

Then run tests:
```bash
# Load from .env (requires additional configuration)
set -a && source .env && set +a  # Linux/macOS
# or use python-dotenv in conftest.py
```

## More Information

- Full documentation: See [README.md](README.md)
- Test structure: See [PyTest DQ Framework/tests/test_examples.py](PyTest DQ Framework/tests/test_examples.py)
- Configuration: See [PyTest DQ Framework/pytest.ini](PyTest DQ Framework/pytest.ini)
