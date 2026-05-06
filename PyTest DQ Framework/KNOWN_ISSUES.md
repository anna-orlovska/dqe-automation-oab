# Known Issues & Real Problems

## ⚠️ Issues That Will Occur During Real Execution

### 1. **Missing Parquet Files** 🔴 CRITICAL
**Problem**: Tests expect real Parquet files in the `parquet_data/` directory
```
parquet_data/
├── patient_sum_treatment_cost_per_facility_type/
├── facility_name_min_time_spent_per_visit_date/
└── facility_type_avg_time_spent_per_visit_date/
```

**Symptoms**:
```
FileNotFoundError: Path does not exist: parquet_data/...
```

**Solution**:
- Generate or download real Parquet files
- Or modify tests to mock data
- Or use SQL to generate data in database

### 2. **Missing Database Tables** 🔴 CRITICAL
**Problem**: Tests expect real `patient_treatment` table in PostgreSQL

**Symptoms**:
```
psycopg2.errors.UndefinedTable: relation "patient_treatment" does not exist
```

**Solution**:
- Run SQL script to create table
- Or add migration/initialization
- Recommendation: Add `init-scripts/` for docker-compose

### 3. **Required Command-Line Parameters** 🟡 IMPORTANT
**Problem**: Tests require mandatory parameters

```bash
# This will NOT work:
pytest tests

# Required:
pytest tests \
  --db_host=localhost \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase
```

**Symptoms**:
```
Error: Missing required option: --db_name
```

**Solution**:
- Document clearly (✓ DONE)
- Or use .env file in conftest.py
- Or set default values (requires caution)

### 4. **Fixture Scope Issues** 🟡 IMPORTANT
**Problem**: In conftest.py:
```python
@pytest.fixture(scope='session')
def db_connection(request):
    connector = PostgresConnectorContextManager(...)
    connection = connector.__enter__()
    yield connection
    connector.__exit__(None, None, None)
```

**Potential Issue**: 
- If one test fails, connection remains open
- No reconnection on error

**Solution**: 
```python
try:
    connector = PostgresConnectorContextManager(...)
    with connector as connection:
        yield connection
except Exception as e:
    pytest.fail(f"Failed: {e}")
```

### 5. **Path Resolution Issues** 🟡 IMPORTANT
**Problem**: Tests have hardcoded paths:

```python
target_path = '../parquet_data/patient_sum_treatment_cost_per_facility_type'
```

**Potential Issue**:
- Path is relative to current directory
- Different results when run from different locations
- Jenkins will run from `PyTest DQ Framework/` directory

**Solution**:
```python
import os
parquet_base = os.path.join(os.path.dirname(__file__), '../../parquet_data')
target_path = os.path.join(parquet_base, 'facility_name...')
```

### 6. **HTML Report Path** 🟡 MODERATE
**Problem**: pytest.ini specifies:
```ini
--html=html_report/report.html
```

**Potential Issue**:
- `html_report/` directory must be created
- Path is relative to execution directory

**Solution**:
```python
# In conftest.py
import os
os.makedirs('html_report', exist_ok=True)
```

### 7. **Type Hints Compatibility** 🟢 MINOR
**Problem**: Uses Python 3.9+ type hints:
```python
def process(file_path: str, include_subfolders: bool = False) -> pd.DataFrame:
```

**Potential Issue**: 
- Not compatible with Python < 3.9

**Solution**: 
- Require Python 3.9+ in requirements.txt (✓ DONE)

---

## 📋 Checklist for Real Execution

### Before Running Tests:
- [ ] Install requirements.txt: `pip install -r requirements.txt`
- [ ] Start Docker: `docker-compose up -d`
- [ ] Wait 30 seconds for PostgreSQL startup
- [ ] Create tables in database (script needed!)
- [ ] Copy/generate Parquet files
- [ ] Create `html_report/` directory

### Running Tests:
```bash
cd "PyTest DQ Framework"

# All parameters are mandatory!
pytest tests \
  --db_host=localhost \
  --db_port=5434 \
  --db_user=myuser \
  --db_password=mypassword \
  --db_name=mydatabase \
  -v
```

### Expected Results:
- ✅ 71 tests should pass
- ✅ HTML report in `html_report/report.html`
- ✅ Allure results in `allure-results/`

---

## 🔧 Recommended Changes

### 1. Add Database Initialization Script
```bash
# init-scripts/01-init-database.sql
CREATE TABLE IF NOT EXISTS patient_treatment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    treatment_cost DECIMAL(10, 2) NOT NULL,
    ...
);
```

### 2. Improve Fixture in conftest.py
```python
@pytest.fixture(scope='session')
def db_connection(request):
    """Improved fixture with better error handling"""
    db_host = request.config.getoption("--db_host")
    db_port = request.config.getoption("--db_port")
    db_name = request.config.getoption("--db_name")
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")

    # Must use context manager
    connector = PostgresConnectorContextManager(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password
    )
    
    try:
        with connector as connection:
            yield connection
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")
```

### 3. Add Path Resolution Helper
```python
# src/utils/path_utils.py
import os

def get_parquet_path(relative_path):
    """Get absolute path to parquet file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, relative_path)
```

### 4. Create .env Handling
```python
# conftest.py
from dotenv import load_dotenv
import os

# Load .env if it exists
load_dotenv()

# Use environment variables as fallback
default_db_host = os.getenv('DB_HOST', 'localhost')
```

---

## 📊 Implementation Readiness

| Component | Status | Issues | Solution |
|-----------|--------|--------|----------|
| Core Modules | ✅ | None | - |
| Fixtures | ⚠️ | Error handling | Add try/except |
| Test Data | ❌ | Missing files | Generate/mock |
| DB Tables | ❌ | Not created | SQL script |
| Path Resolution | ⚠️ | Relative paths | os.path.join() |
| HTML Report | ⚠️ | Directory missing | Create in conftest |
| Parameters | ✅ | Required args | Document (done) |

---

## 🚨 Critical Path to Working Tests

**Prerequisite** (must have):
1. PostgreSQL running with `mydatabase` created
2. Table `patient_treatment` with sample data
3. Parquet files in `parquet_data/` directory

**Once prerequisites met:**
1. Install: `pip install -r requirements.txt`
2. Run: `pytest tests --db_host=... --db_user=... --db_password=... --db_name=...`
3. Should see: 71 tests passing

---

## 📝 Summary

**Framework code**: ✅ Syntactically correct
**Framework config**: ⚠️ Requires external setup
**Test data**: ❌ Must be provided externally
**Documentation**: ✅ Complete

**Real Status**: Framework will NOT work without:
1. Real PostgreSQL database with tables
2. Real Parquet files in parquet_data/
3. Running Docker containers
4. Proper command-line parameters
