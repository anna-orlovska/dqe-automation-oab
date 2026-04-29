# Comprehensive Validation Guide

Final validation checklist to ensure all PyTest DQ Framework components are functioning correctly.

## Table of Contents

- [Pre-Validation Setup](#pre-validation-setup)
- [Component Validation](#component-validation)
- [Local Testing Validation](#local-testing-validation)
- [Report Generation Validation](#report-generation-validation)
- [Jenkins Pipeline Validation](#jenkins-pipeline-validation)
- [Validation Checklist](#validation-checklist)
- [Troubleshooting Validation Failures](#troubleshooting-validation-failures)

## Pre-Validation Setup

### Prerequisites Check

```bash
# Verify Python installation
python3 --version  # Should be 3.9+

# Verify Docker installation
docker --version
docker-compose --version

# Verify Git
git --version

# Navigate to project root
cd "path/to/DQE_Framework"

# List directory structure
ls -la
```

Expected output should include:
```
PyTest DQ Framework/
docker-compose.yml
README.md
QUICKSTART.md
JENKINS_SETUP.md
REPORTING.md
CI_CD_GUIDE.md
VALIDATION.md
```

### Environment Preparation

```bash
# Activate virtual environment
source venv_3.13/bin/activate  # Linux/macOS
# or
venv_3.13\Scripts\activate     # Windows

# Verify environment
which python3  # Should point to venv
pip list | grep pytest
```

## Component Validation

### 1. Validate Core Modules

```bash
# Test PostgresConnectorContextManager
python3 << 'EOF'
from connectors.postgres.postgres_connector import PostgresConnectorContextManager
print("✓ PostgresConnectorContextManager imported successfully")

# Check methods exist
connector = PostgresConnectorContextManager(
    db_host="localhost",
    db_port=5434,
    db_name="test",
    db_user="test",
    db_password="test"
)
assert hasattr(connector, '__enter__'), "Missing __enter__ method"
assert hasattr(connector, '__exit__'), "Missing __exit__ method"
assert hasattr(connector, 'get_data_sql'), "Missing get_data_sql method"
print("✓ PostgresConnectorContextManager has all required methods")
EOF
```

### 2. Validate ParquetReader

```bash
python3 << 'EOF'
from connectors.file_system.parquet_reader import ParquetReader
print("✓ ParquetReader imported successfully")

# Check method exists
assert hasattr(ParquetReader, 'process'), "Missing process method"
print("✓ ParquetReader has process method")

# Check method signature
import inspect
sig = inspect.signature(ParquetReader.process)
assert 'file_path' in sig.parameters, "Missing file_path parameter"
assert 'include_subfolders' in sig.parameters, "Missing include_subfolders parameter"
print("✓ ParquetReader.process has correct signature")
EOF
```

### 3. Validate DataQualityLibrary

```bash
python3 << 'EOF'
from data_quality.data_quality_validation_library import DataQualityLibrary
import pandas as pd

print("✓ DataQualityLibrary imported successfully")

# Check all required methods exist
required_methods = [
    'check_dataset_is_not_empty',
    'check_count',
    'check_data_completeness',
    'check_duplicates',
    'check_not_null_values',
    'check_consistency'
]

dq = DataQualityLibrary()
for method in required_methods:
    assert hasattr(dq, method), f"Missing method: {method}"
    print(f"  ✓ {method} exists")

# Test basic functionality
test_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
dq.check_dataset_is_not_empty(test_df)
print("✓ DataQualityLibrary basic functionality works")
EOF
```

### 4. Validate pytest Configuration

```bash
cd "PyTest DQ Framework"

# Check pytest.ini exists
test -f pytest.ini && echo "✓ pytest.ini exists" || echo "✗ pytest.ini missing"

# Verify markers are registered
pytest --markers | grep -E "smoke|completeness|quality|parquet_data"
echo "✓ All markers registered"

# Check conftest.py exists
test -f tests/conftest.py && echo "✓ conftest.py exists" || echo "✗ conftest.py missing"
```

## Local Testing Validation

### 1. Start Infrastructure

```bash
# Start containers
docker-compose up -d

# Wait for services
sleep 10

# Verify services are running
docker ps | grep -E "postgres|jenkins"
echo "✓ Infrastructure started"

# Check PostgreSQL is responding
docker exec postgres pg_isready -U myuser -d mydatabase
echo "✓ PostgreSQL is responding"
```

### 2. Test Database Connection

```bash
cd "PyTest DQ Framework"

# Run connection test
pytest tests/dq\ checks/parquet_files/test_smoke_basic_structure.py::TestDatabaseConnectivity::test_database_connection_established \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Should pass with green checkmark
```

### 3. Test Data Retrieval

```bash
cd "PyTest DQ Framework"

# Run data retrieval test
pytest tests/dq\ checks/parquet_files/test_smoke_basic_structure.py::TestDatabaseConnectivity::test_can_fetch_data \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Should show data fetched successfully
```

### 4. Run Smoke Tests

```bash
cd "PyTest DQ Framework"

# Run all smoke tests
pytest tests -m smoke \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Expected: 10+ passing tests
```

### 5. Run Completeness Tests

```bash
cd "PyTest DQ Framework"

pytest tests -m completeness \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Expected: 8+ passing tests
```

### 6. Run Quality Tests

```bash
cd "PyTest DQ Framework"

pytest tests -m quality \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Expected: 12+ passing tests
```

### 7. Run All Tests

```bash
cd "PyTest DQ Framework"

pytest tests \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v

# Expected: 30+ passing tests
# Success rate should be 100%
```

## Report Generation Validation

### 1. Validate HTML Report Generation

```bash
cd "PyTest DQ Framework"

# Generate HTML report
pytest tests \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    --html=../html_report/report.html \
    --self-contained-html

# Verify file exists
test -f html_report/report.html && echo "✓ HTML report generated" || echo "✗ HTML report missing"

# Check file size
ls -lh html_report/report.html
# Should be > 100KB

# Verify content
grep -q "passed" html_report/report.html && echo "✓ HTML report contains test results"
```

### 2. Validate Allure Report Generation

```bash
cd "PyTest DQ Framework"

# Clean previous results
rm -rf allure-results

# Generate Allure results
pytest tests \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    --alluredir=../allure-results

# Verify results directory
test -d allure-results && echo "✓ Allure results directory created"

# Verify JSON files exist
test "$(ls allure-results/*.json 2>/dev/null | wc -l)" -gt 0 && echo "✓ Allure JSON results generated"

# Count results
ls allure-results/*.json | wc -l
# Should be 30+ files (one per test + categories.json)
```

### 3. Validate Report Structure

```bash
# Check HTML report structure
grep -E "<title|<body|class=\".*(passed|failed)\"" html_report/report.html | head -5

# Check Allure results have test data
cat allure-results/*-result.json | head -20

# Verify both reports have content
echo "HTML Report size: $(du -h html_report/report.html | cut -f1)"
echo "Allure Results: $(ls -1 allure-results/*.json | wc -l) files"
```

## Jenkins Pipeline Validation

### 1. Verify Jenkinsfile Syntax

```bash
# Check Jenkinsfile exists
test -f "PyTest DQ Framework/Jenkinsfile" && echo "✓ Jenkinsfile exists"

# Verify Groovy syntax (requires Jenkins Groovy linter)
# Or validate manually
grep -E "pipeline|stages|stage|steps" "PyTest DQ Framework/Jenkinsfile" | head -5
```

### 2. Check Jenkins Credentials

```bash
# Verify Jenkins is running
docker logs jenkins | grep -i "jenkins.*started"

# Access Jenkins API to verify setup
curl -s http://localhost:8080/jenkins/api/json | jq '.jobs' 2>/dev/null || echo "Jenkins API available"

# Verify credentials exist (requires authentication)
# curl -u admin:password http://localhost:8080/jenkins/credentials/api/json
```

### 3. Trigger Manual Pipeline Run

```bash
# Via Jenkins UI:
# 1. Navigate to job
# 2. Click "Build Now"
# 3. Monitor Console Output
# 4. Wait for completion

# Via curl (with authentication):
# curl -X POST http://localhost:8080/jenkins/job/DQ_Tests/build \
#   --user admin:password

echo "✓ Trigger pipeline via Jenkins UI"
```

### 4. Verify Pipeline Execution

After pipeline completes:

```bash
# Check build artifacts
docker exec jenkins ls -la /var/jenkins_home/jobs/DQ_Tests_Pipeline/builds/lastBuild/

# Verify reports were generated
docker exec jenkins test -f /var/jenkins_home/jobs/DQ_Tests_Pipeline/builds/lastBuild/archive/html_report/report.html
echo "✓ HTML report archived in Jenkins"

# View build log
docker exec jenkins cat /var/jenkins_home/jobs/DQ_Tests_Pipeline/builds/lastBuild/log | tail -50
```

### 5. Verify Report Publishing

```bash
# Check published HTML report
curl -s http://localhost:8080/jenkins/job/DQ_Tests_Pipeline/lastBuild/PyTest_DQ_Report/ | grep -q "passed"
echo "✓ HTML report published in Jenkins"

# Check Allure report (if Allure plugin installed)
curl -s http://localhost:8080/jenkins/job/DQ_Tests_Pipeline/allure/ 2>/dev/null | grep -q "allure"
echo "✓ Allure report published in Jenkins"
```

## Validation Checklist

Complete validation by checking all items:

### Infrastructure ✅
- [ ] Docker and Docker Compose installed
- [ ] Docker containers started (`docker ps` shows postgres and jenkins)
- [ ] PostgreSQL responding to health check
- [ ] Jenkins UI accessible at `http://localhost:8080`

### Core Modules ✅
- [ ] PostgresConnectorContextManager imports correctly
- [ ] PostgresConnectorContextManager has all methods
- [ ] ParquetReader imports and has process method
- [ ] DataQualityLibrary imports and has all 6 methods
- [ ] Basic DataQualityLibrary functionality works

### Configuration ✅
- [ ] pytest.ini exists and is valid
- [ ] conftest.py exists with fixtures
- [ ] All pytest markers are registered
- [ ] requirements.txt has all dependencies

### Local Testing ✅
- [ ] Database connection test passes
- [ ] Data retrieval test passes
- [ ] Smoke tests pass (10+ tests)
- [ ] Completeness tests pass (8+ tests)
- [ ] Quality tests pass (12+ tests)
- [ ] Overall test success rate is 100%

### Report Generation ✅
- [ ] HTML report generated
- [ ] HTML report contains test results
- [ ] HTML report is self-contained (single file)
- [ ] Allure results directory created
- [ ] Allure JSON files generated (30+ files)
- [ ] Both reports have valid content

### Jenkins Setup ✅
- [ ] Jenkinsfile exists and is valid
- [ ] POSTGRES_SECRET credential created in Jenkins
- [ ] Pipeline job created
- [ ] Pipeline job can be triggered

### Jenkins Execution ✅
- [ ] Pipeline can be triggered manually
- [ ] Pipeline successfully executes all stages
- [ ] HTML report published in Jenkins
- [ ] Allure report published in Jenkins (if plugin installed)
- [ ] Build logs show successful test execution

### Documentation ✅
- [ ] README.md is complete
- [ ] QUICKSTART.md is available
- [ ] DEVELOPMENT.md provides guidance
- [ ] JENKINS_SETUP.md explains credentials setup
- [ ] REPORTING.md explains report generation
- [ ] CI_CD_GUIDE.md explains pipeline integration

## Troubleshooting Validation Failures

### Test Connection Failures

**Symptom**: "Could not connect to PostgreSQL"

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection manually
psql -h localhost -p 5434 -U myuser -d mydatabase

# If fails, restart
docker-compose down
docker-compose up -d
```

### Missing Fixtures

**Symptom**: "fixture 'db_connection' not found"

```bash
# Verify conftest.py exists
ls "PyTest DQ Framework/tests/conftest.py"

# Check fixture definitions
grep -n "@pytest.fixture" "PyTest DQ Framework/tests/conftest.py"

# Verify fixture scope
grep -n "scope=" "PyTest DQ Framework/tests/conftest.py"
```

### Import Errors

**Symptom**: "ModuleNotFoundError: No module named 'connectors'"

```bash
# Verify src is marked as source root in IDE
# Or verify PYTHONPATH includes src

# Check imports in tests
cd "PyTest DQ Framework"
python3 -c "from connectors.postgres.postgres_connector import PostgresConnectorContextManager"
```

### Report Not Generated

**Symptom**: "No reports generated"

```bash
# Check pytest-html is installed
pip list | grep pytest-html

# Verify path is writable
mkdir -p html_report
ls -la html_report

# Run with explicit output
pytest tests --html=report.html -v
```

### Jenkins Build Failures

**Symptom**: "Build failed in Jenkins"

```bash
# Check Jenkins logs
docker logs jenkins | tail -50

# Check build console
# Jenkins UI → Job → Build → Console Output

# Verify credentials
# Jenkins → Credentials → Global → POSTGRES_SECRET should exist

# Test locally first
cd "PyTest DQ Framework"
pytest tests --db_host=localhost --db_user=myuser --db_password=mypassword --db_name=mydatabase
```

## Automated Validation Script

Run complete validation:

```bash
#!/bin/bash
set -e

echo "========== PyTest DQ Framework Validation =========="
echo

# Check prerequisites
echo "[1/5] Checking prerequisites..."
python3 --version
docker --version
docker-compose --version
echo "✓ Prerequisites OK"
echo

# Start infrastructure
echo "[2/5] Starting infrastructure..."
docker-compose up -d
sleep 10
docker ps | grep -E "postgres|jenkins"
docker exec postgres pg_isready -U myuser
echo "✓ Infrastructure OK"
echo

# Run tests
echo "[3/5] Running tests..."
cd "PyTest DQ Framework"
pytest tests \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    -v --tb=short
echo "✓ Tests OK"
echo

# Generate reports
echo "[4/5] Generating reports..."
pytest tests \
    --db_host=localhost \
    --db_port=5434 \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    --html=../html_report/report.html \
    --self-contained-html \
    --alluredir=../allure-results
echo "✓ Reports OK"
echo

# Verify reports
echo "[5/5] Verifying reports..."
test -f ../html_report/report.html && echo "✓ HTML report exists"
test "$(ls ../allure-results/*.json 2>/dev/null | wc -l)" -gt 0 && echo "✓ Allure results exist"
echo

echo "========== Validation Complete =========="
echo "All checks passed! Framework is ready for use."
```

## Success Criteria

All of the following must be true:

✅ All 30+ tests pass locally
✅ HTML report generated successfully
✅ Allure results generated successfully
✅ Docker containers are running
✅ Jenkins pipeline triggers successfully
✅ Pipeline execution completes without errors
✅ Reports are published in Jenkins
✅ All documentation is complete and accessible

## Next Steps

After successful validation:

1. **Deploy to Production**: Use Jenkins pipeline for automated testing
2. **Monitor Results**: Track test metrics and trends
3. **Extend Tests**: Add more specific tests for your data
4. **Optimize**: Fine-tune performance and reporting
5. **Share**: Distribute framework with team

## Support

If validation fails:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (if created)
2. Review [README.md](README.md) for setup instructions
3. Check [DEVELOPMENT.md](DEVELOPMENT.md) for debugging
4. Review [JENKINS_SETUP.md](JENKINS_SETUP.md) for Jenkins issues
5. Review [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for pipeline issues
