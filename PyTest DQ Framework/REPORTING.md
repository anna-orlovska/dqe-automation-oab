# Test Reporting Guide

Complete guide for HTML and Allure test report generation in PyTest DQ Framework.

## Table of Contents

- [HTML Reports](#html-reports)
- [Allure Reports](#allure-reports)
- [Jenkins Integration](#jenkins-integration)
- [Report Configuration](#report-configuration)
- [Viewing Reports](#viewing-reports)
- [CI/CD Pipeline](#cicd-pipeline)

## HTML Reports

### Generate HTML Report Locally

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

### HTML Report Features

- **Self-contained**: Single HTML file with all assets embedded
- **Test Results**: Passed, failed, skipped tests
- **Execution Time**: Duration for each test and overall
- **Error Details**: Full traceback for failed tests
- **Test Markers**: Display applied pytest markers
- **Environment Info**: Python version, pytest version, plugins

### HTML Report Output Structure

```
html_report/
└── report.html              # Main report file
```

### Using Makefile

```bash
make test-report    # Run tests and generate HTML report
```

### Report Configuration

In `pytest.ini`:

```ini
addopts =
    -v
    --html=html_report/report.html
    --self-contained-html
```

### View HTML Report

1. Open `html_report/report.html` in browser
2. Or from Jenkins:
   - Click **PyTest DQ Report** link in build page

## Allure Reports

### What is Allure?

Allure is a comprehensive testing tool that provides:
- **Beautiful Reports**: Interactive HTML reports
- **Test History**: Track test results over time
- **Test Analytics**: Identify flaky tests
- **Behavior Mapping**: Organize tests by features/stories
- **Defect Management**: Link tests to defects

### Installation

```bash
# Already in requirements.txt
pip install allure-pytest==2.15.3
pip install allure-python-commons==2.15.3

# Also need allure-commandline for viewing reports
# Windows
choco install allure

# macOS
brew install allure

# Linux
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

### Generate Allure Results

```bash
cd "PyTest DQ Framework"
pytest tests \
    --db_host=localhost \
    --db_user=myuser \
    --db_password=mypassword \
    --db_name=mydatabase \
    --alluredir=../allure-results
```

### Allure Results Structure

```
allure-results/
├── 0-result.json
├── 1-result.json
├── 2-result.json
├── ...
└── categories.json
```

Each test generates a JSON file with detailed information.

### Generate and View Allure Report

```bash
# Generate from results
allure serve allure-results

# Or generate to directory
allure generate allure-results --clean -o allure-report
open allure-report/index.html
```

### Using Makefile

```bash
make test-allure    # Run tests and generate Allure results
```

## Allure Decorators

### Test Description

```python
@pytest.mark.description("Verify patient ID is positive integer")
def test_patient_id_positive(self, source_data):
    """Test description."""
    pass
```

### Features and Stories

```python
@allure.feature("Data Validation")
@allure.story("Patient Data")
def test_patient_id_positive(self, source_data):
    """Test description."""
    pass
```

Requires import:
```python
import allure
```

### Severity

```python
@allure.severity(allure.severity_level.CRITICAL)
def test_critical_feature(self):
    pass

@allure.severity(allure.severity_level.MINOR)
def test_minor_feature(self):
    pass
```

Severity levels:
- `BLOCKER`
- `CRITICAL`
- `NORMAL` (default)
- `MINOR`
- `TRIVIAL`

### Add Steps

```python
@allure.step("Check dataset is not empty")
def check_empty(df):
    assert len(df) > 0

def test_data(self, data_quality_library, source_data):
    """Test with steps."""
    with allure.step("Load source data"):
        assert source_data is not None
    
    with allure.step("Validate completeness"):
        data_quality_library.check_data_completeness(source_data)
```

### Link to Issues

```python
@allure.link("https://github.com/your-org/your-repo/issues/123")
def test_feature(self):
    pass

@allure.issue("JIRA-1234")
def test_jira_issue(self):
    pass
```

### Example Test with Allure Decorators

```python
"""
Description: Patient treatment cost validation.
Requirement(s): FRAMEWORK-014
Author(s): QA Team
"""

import pytest
import allure


@allure.feature("Data Quality")
@allure.story("Treatment Costs")
class TestTreatmentCosts:
    """Treatment cost validation tests."""

    @pytest.mark.quality
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Verify treatment costs are not negative")
    @allure.issue("JIRA-5678")
    def test_treatment_cost_positive(self, source_data):
        """Verify all treatment costs are positive."""
        with allure.step("Filter negative costs"):
            negative = source_data[source_data['treatment_cost'] < 0]
        
        with allure.step("Assert no negative costs"):
            assert len(negative) == 0, f"Found {len(negative)} negative costs"
```

## Jenkins Integration

### Configure HTML Report Publishing

In Jenkinsfile:

```groovy
stage('Publish HTML Report') {
    steps {
        publishHTML target: [
            reportDir: "${REPORTS_DIR}",
            reportFiles: 'report.html',
            reportName: 'PyTest DQ Report',
            keepAll: true,
            alwaysLinkToLastBuild: true
        ]
    }
}
```

### Archive Artifacts

```groovy
stage('Archive Reports') {
    steps {
        archiveArtifacts artifacts: 'html_report/**,allure-results/**',
                          allowEmptyArchive: true,
                          fingerprint: true
    }
}
```

### Configure Allure Plugin (Optional)

1. Install Allure Plugin in Jenkins:
   - **Manage Jenkins** → **Manage Plugins**
   - Search "Allure"
   - Install "Allure Plugin"
   - Restart Jenkins

2. Add Allure Report Stage:

```groovy
stage('Publish Allure Report') {
    steps {
        allure([
            includeProperties: false,
            jdk: '',
            reportBuildPolicy: 'ALWAYS',
            results: [[path: 'allure-results']]
        ])
    }
}
```

## Report Configuration

### HTML Report Options

```python
# In pytest.ini
addopts =
    --html=html_report/report.html
    --self-contained-html
    --html-self-contained-html    # Alternative syntax
```

Options:
- `--html=path` - Output file path
- `--self-contained-html` - Embed all CSS/JS in single file
- `--html-report=path` - Alternative option name

### Allure Report Options

```python
# In pytest.ini
addopts =
    --alluredir=allure-results
    --allure-no-history          # Don't track history
```

Options:
- `--alluredir=path` - Results directory
- `--allure-no-history` - Don't save history

### Custom HTML Report CSS

Create custom CSS file:

```css
/* pytest-html-custom.css */
body {
    font-family: 'Arial', sans-serif;
}

.passed {
    color: green;
}

.failed {
    color: red;
}
```

Then configure in conftest.py:

```python
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "quality: mark test as quality test"
    )
```

## Viewing Reports

### HTML Report in Browser

```bash
# Open in default browser
open html_report/report.html          # macOS
xdg-open html_report/report.html      # Linux
start html_report/report.html         # Windows

# Or open manually in browser
# File → Open → navigate to html_report/report.html
```

### Allure Report Dashboard

```bash
# Interactive view with live updates
allure serve allure-results

# Or static HTML
allure generate allure-results --clean -o allure-report
open allure-report/index.html
```

### Allure Report Features

- **Overview**: Test summary and history
- **Behaviors**: Tests organized by features/stories
- **Defects**: Failed tests and issues
- **Timeline**: Test execution timeline
- **History**: Test results over time

## CI/CD Pipeline

### Complete Report Generation Pipeline

```groovy
pipeline {
    agent any

    environment {
        REPORTS_DIR = 'html_report'
        ALLURE_DIR = 'allure-results'
    }

    stages {
        stage('Run Tests with Reports') {
            steps {
                sh '''
                    cd "PyTest DQ Framework"
                    pytest tests \
                        --db_host=${DB_HOST} \
                        --db_port=${DB_PORT} \
                        --db_user=${DB_USER} \
                        --db_password=${DB_PASSWORD} \
                        --db_name=${DB_NAME} \
                        --html=../${REPORTS_DIR}/report.html \
                        --self-contained-html \
                        --alluredir=../${ALLURE_DIR} \
                        -v || true
                '''
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: '${REPORTS_DIR}/**,${ALLURE_DIR}/**',
                                  allowEmptyArchive: true,
                                  fingerprint: true
            }
        }

        stage('Publish HTML Report') {
            steps {
                publishHTML target: [
                    reportDir: "${REPORTS_DIR}",
                    reportFiles: 'report.html',
                    reportName: 'PyTest DQ Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ]
            }
        }

        stage('Publish Allure Report') {
            when {
                fileExists('allure-results')
            }
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: '${ALLURE_DIR}']]
                ])
            }
        }
    }

    post {
        always {
            echo 'Test execution completed'
            echo "HTML Report: ${REPORTS_DIR}/report.html"
            echo "Allure Results: ${ALLURE_DIR}"
        }
    }
}
```

## Test Result Analysis

### Using HTML Reports

1. **Test Summary**
   - Total tests: Passed/Failed/Skipped counts
   - Execution time: Total and per test
   - Success rate: Percentage of passing tests

2. **Failed Tests**
   - Test name and class
   - Failure message and traceback
   - Duration

3. **Test Markers**
   - View which markers were applied
   - Filter by marker

### Using Allure Reports

1. **Overview Tab**
   - Test statistics
   - Duration chart
   - Status breakdown

2. **Behaviors Tab**
   - Tests organized by feature/story
   - Feature status and duration
   - Search and filter

3. **Defects Tab**
   - Failed tests with details
   - Error types and frequency
   - Linked issues

4. **Timeline Tab**
   - Test execution order
   - Concurrent test visibility
   - Performance analysis

5. **History Tab**
   - Test results over time
   - Trend analysis
   - Flaky test detection

## Report Retention

### Local Development

```bash
# Keep reports for review
mkdir -p html_report
mkdir -p allure-results

# Or clean before new run
rm -rf html_report/*
rm -rf allure-results/*
pytest ...
```

### Jenkins

```groovy
// Keep last 30 builds
buildDiscarder(logRotator(numToKeepStr: '30'))

// Keep artifacts forever
publishHTML target: [
    keepAll: true,
    alwaysLinkToLastBuild: true
    ...
]
```

## Export Reports

### Export HTML Report

```bash
# Copy report file
cp html_report/report.html /path/to/export/

# Or open and print to PDF
open html_report/report.html
# Print → Save as PDF
```

### Export Allure Results

```bash
# Generate and export
allure generate allure-results --clean -o /path/to/export/allure-report

# Share the directory
zip -r allure-report.zip /path/to/export/allure-report
```

## Troubleshooting

### Issue: HTML Report Not Generated

**Solution:**
```bash
# Check pytest-html is installed
pip list | grep pytest-html

# Verify path is writable
mkdir -p html_report
ls -la html_report

# Run with explicit path
pytest tests --html=./html_report/report.html --self-contained-html
```

### Issue: Allure Report Empty

**Solution:**
```bash
# Check results were generated
ls -la allure-results/

# Check JSON files exist
find allure-results -name "*.json" -type f

# Run allure with verbose
allure serve allure-results --verbose
```

### Issue: Jenkins Can't Find Report

**Solution:**
```groovy
// Verify file exists before publishing
sh 'test -f ${REPORTS_DIR}/report.html'

// Or use glob pattern
archiveArtifacts artifacts: '**/report.html',
                  allowEmptyArchive: true
```

## Best Practices

### 1. Always Generate Reports

```bash
# Include in all test runs
pytest tests --html=report.html --alluredir=allure-results
```

### 2. Use Decorators for Better Organization

```python
@allure.feature("Feature Name")
@allure.story("Story Name")
@allure.severity(allure.severity_level.CRITICAL)
def test_something(self):
    pass
```

### 3. Archive Reports in CI/CD

```groovy
// Never skip report archiving
post {
    always {
        archiveArtifacts artifacts: '**/*.html,allure-results/**'
    }
}
```

### 4. Keep Report History

```groovy
// Set Jenkins to keep old reports
buildDiscarder(logRotator(numToKeepStr: '30'))
publishHTML target: [keepAll: true]
```

### 5. Link Reports to Issue Trackers

```python
@allure.issue("JIRA-1234")
def test_jira_issue(self):
    pass
```

## References

- [pytest-html Documentation](https://pytest-html.readthedocs.io/)
- [Allure Documentation](https://docs.qameta.io/allure/)
- [Allure Python Documentation](https://github.com/allure-framework/allure-python)
- [Jenkins HTML Publisher Plugin](https://plugins.jenkins.io/htmlpublisher/)
