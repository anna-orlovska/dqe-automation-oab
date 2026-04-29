# CI/CD Integration Guide

Complete guide for integrating PyTest DQ Framework with Jenkins CI/CD pipeline.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup Steps](#setup-steps)
- [Pipeline Execution](#pipeline-execution)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Overview

The PyTest DQ Framework is designed for seamless CI/CD integration with Jenkins, featuring:

- **Automated Testing**: Scheduled or event-triggered test runs
- **Multi-Stage Pipeline**: Modular pipeline stages for flexibility
- **Report Generation**: HTML and Allure test reports
- **Artifact Management**: Automatic report archiving and publishing
- **Credentials Management**: Secure database credentials
- **Docker Support**: Containerized PostgreSQL and Jenkins

## Architecture

### CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Jenkins Pipeline                         │
└─────────────────────────────────────────────────────────────┘
         │
         ├─→ Checkout (Git)
         │   └─→ Clone repository
         │
         ├─→ Install Dependencies
         │   ├─→ Create venv
         │   └─→ pip install requirements.txt
         │
         ├─→ Run Tests
         │   ├─→ Smoke Tests
         │   ├─→ Completeness Tests
         │   └─→ Quality Tests
         │
         ├─→ Generate Reports
         │   ├─→ HTML Report (pytest-html)
         │   └─→ Allure Results
         │
         ├─→ Archive Artifacts
         │   ├─→ HTML Reports
         │   └─→ Allure Results
         │
         └─→ Publish Reports
             ├─→ Publish HTML Report
             └─→ Publish Allure Report

┌─────────────────────────────────────────────────────────────┐
│              Infrastructure (Docker)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Jenkins LTS     │         │  PostgreSQL 15   │         │
│  │  Port: 8080      │────────→│  Port: 5432      │         │
│  │  Agent: 50000    │         │  Network: bridge │         │
│  └──────────────────┘         └──────────────────┘         │
│         (Shared Network: tafordqenetwork)                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships

```
Git Repository
    ↓
    └─→ Jenkinsfile (Pipeline definition)
           ↓
           ├─→ Environment Variables
           │   └─→ Credentials (POSTGRES_SECRET)
           ├─→ Stages
           │   └─→ PyTest Framework
           │       └─→ conftest.py (fixtures + database connection)
           └─→ Reports
               ├─→ HTML Reports
               └─→ Allure Reports
```

## Setup Steps

### Step 1: Start Infrastructure

```bash
# Start Jenkins and PostgreSQL containers
docker-compose up -d

# Verify both services are running
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                  STATUS    PORTS
abc123         jenkins/jenkins:lts    Up ...    0.0.0.0:8080->8080/tcp
def456         postgres:15            Up ...    0.0.0.0:5434->5432/tcp
```

### Step 2: Configure Jenkins

Follow [JENKINS_SETUP.md](JENKINS_SETUP.md):

1. **Initial Access**
   - Get initial password
   - Login with admin credentials
   - Install suggested plugins

2. **Create Credentials**
   - Add `POSTGRES_SECRET` credential
   - ID: `POSTGRES_SECRET` (must match Jenkinsfile)
   - Username: `myuser`
   - Password: `mypassword`

3. **Create Pipeline Job**
   - Job type: Pipeline
   - Pipeline from SCM: Git
   - Repository: Your GitHub URL
   - Credentials: GitHub credentials (if private)
   - Script Path: `PyTest DQ Framework/Jenkinsfile`

### Step 3: Configure Git Repository

```bash
# Clone repository
git clone https://github.com/your-org/your-repo.git

# Ensure Jenkinsfile exists
ls "PyTest DQ Framework/Jenkinsfile"
```

### Step 4: Verify Pipeline Configuration

The Jenkinsfile should contain:

```groovy
environment {
    POSTGRES_CREDENTIALS = credentials('POSTGRES_SECRET')
    DB_HOST = 'postgres'
    DB_PORT = '5432'
    DB_NAME = 'mydatabase'
    DB_USER = "${POSTGRES_CREDENTIALS_USR}"
    DB_PASSWORD = "${POSTGRES_CREDENTIALS_PSW}"
}
```

### Step 5: Run First Pipeline

1. Open Jenkins job
2. Click **Build Now**
3. Monitor in Build History
4. View Console Output for logs
5. After completion, access reports

## Pipeline Execution

### Manual Execution

```bash
# From Jenkins UI
1. Navigate to job
2. Click "Build Now"
3. Monitor progress in Build History
```

### Scheduled Execution

Configure in Job Configuration:

```
Build Triggers:
- Poll SCM: H H * * *  (Daily)
- GitHub webhook: Trigger on push
```

### View Execution Details

```bash
# Via curl
curl http://localhost:8080/jenkins/job/DQ_Tests_Pipeline/lastBuild/consoleText

# Via Jenkins UI
1. Click build number
2. Click "Console Output"
```

### Test Execution Environment

Inside Jenkins:

```
Host: postgres (Docker network hostname)
Port: 5432 (internal container port)
Database: mydatabase
User: myuser
Password: (from POSTGRES_SECRET credential)
```

### Report Access

After pipeline completes:

1. **HTML Report**
   - Jenkins job page → Click "PyTest DQ Report"
   - Or: Build page → Artifact → html_report/report.html

2. **Allure Report**
   - Jenkins job page → Click "Allure Report"
   - Or: Build page → Review Allure results

## Monitoring and Maintenance

### Monitor Pipeline Execution

```bash
# View Jenkins logs
docker logs -f jenkins

# View PostgreSQL logs
docker logs -f postgres

# Check pipeline status
curl http://localhost:8080/jenkins/job/DQ_Tests_Pipeline/api/json | jq '.lastBuild'
```

### Track Test Trends

1. **HTML Reports**
   - View previous builds
   - Compare test counts
   - Track failure patterns

2. **Allure Reports**
   - View trend charts
   - Analyze test history
   - Identify flaky tests

### Backup Reports

```bash
# Backup Jenkins configuration
docker cp jenkins:/var/jenkins_home/jobs ./jenkins_backup_$(date +%Y%m%d)

# Backup test results
cp -r html_report html_report_backup_$(date +%Y%m%d)
cp -r allure-results allure_backup_$(date +%Y%m%d)
```

### Maintain Pipeline

```bash
# Keep Jenkins up to date
docker-compose pull

# Restart services
docker-compose restart

# Full restart
docker-compose down && docker-compose up -d
```

## Advanced Configuration

### Parallel Test Execution

```groovy
stage('Run Tests') {
    parallel {
        stage('Smoke Tests') {
            steps {
                sh 'pytest tests -m smoke ...'
            }
        }
        stage('Quality Tests') {
            steps {
                sh 'pytest tests -m quality ...'
            }
        }
    }
}
```

### Conditional Report Publishing

```groovy
stage('Publish Reports') {
    when {
        always()  // Always publish
    }
    steps {
        publishHTML target: [...]
    }
}
```

### Email Notifications

```groovy
post {
    failure {
        emailext(
            subject: 'DQ Tests Failed',
            body: 'See console output',
            to: 'team@example.com'
        )
    }
}
```

### Webhook Integration

```groovy
stage('Notify Slack') {
    steps {
        slackSend(
            color: 'good',
            message: 'DQ Tests passed!'
        )
    }
}
```

## Troubleshooting

### Issue: "Connection refused to PostgreSQL"

**Symptoms:**
```
ERROR: could not connect to server
```

**Solution:**
```bash
# Verify containers are running
docker ps | grep postgres

# Check network
docker network inspect tafordqenetwork

# Verify hostname in Jenkinsfile
grep "DB_HOST" PyTest\ DQ\ Framework/Jenkinsfile  # Should be 'postgres'

# Restart services
docker-compose down && docker-compose up -d
```

### Issue: "POSTGRES_SECRET not found"

**Symptoms:**
```
ERROR: POSTGRES_SECRET not found
```

**Solution:**
1. Verify credential exists in Jenkins
2. Check ID is exactly `POSTGRES_SECRET`
3. Recreate credential if needed
4. Verify Jenkinsfile references correct ID

### Issue: "tests not found" error

**Symptoms:**
```
ERROR: no tests ran
```

**Solution:**
```bash
# Check test file paths
find "PyTest DQ Framework/tests" -name "test_*.py"

# Verify script path in Jenkins
# Should be: PyTest DQ Framework/Jenkinsfile

# Check conftest.py exists
ls "PyTest DQ Framework/tests/conftest.py"
```

### Issue: Reports not generated

**Symptoms:**
```
ERROR: Report directory empty
```

**Solution:**
```groovy
// In Jenkinsfile
sh '''
    # Debug: list all files
    find . -name "*.html" -o -name "*.json"
    
    # Verify path
    ls -la html_report/
    ls -la allure-results/
'''
```

### Issue: Jenkins timeout

**Symptoms:**
```
Timeout waiting for test execution
```

**Solution:**
```groovy
options {
    timeout(time: 2, unit: 'HOURS')  // Increase timeout
}
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
# Change "8080:8080" to "8081:8080"
```

## Performance Optimization

### Reduce Test Execution Time

```bash
# Run only smoke tests in CI/CD
pytest tests -m smoke --db_host=postgres ...

# Run parallel tests
pytest tests -n auto --db_host=postgres ...

# Skip long-running tests in some branches
if [ "$BRANCH" = "develop" ]; then
    pytest tests -m "not slow"
fi
```

### Optimize Docker Build

```dockerfile
# Use lightweight base image
FROM jenkins/jenkins:lts-alpine
FROM postgres:15-alpine
```

### Cache Dependencies

```groovy
stage('Install Dependencies') {
    steps {
        // Cache pip packages
        sh '''
            pip install --cache-dir .pip-cache -r requirements.txt
        '''
    }
}
```

## Security Best Practices

### 1. Secure Credentials

✅ Use Jenkins Credentials API
✅ Never log credentials
✅ Rotate passwords regularly
✅ Use strong passwords

### 2. Network Security

✅ Use Docker network isolation
✅ Don't expose services unnecessarily
✅ Use firewall rules

### 3. Access Control

✅ Enable Jenkins authentication
✅ Configure user roles
✅ Limit job access

## Integration with Issue Trackers

### Link to GitHub Issues

```python
@allure.link("https://github.com/your-org/repo/issues/123")
def test_feature(self):
    pass
```

### Link to JIRA

```python
@allure.issue("JIRA-1234")
def test_jira_issue(self):
    pass
```

Configure in allure.properties:
```properties
allure.link.issue.pattern=https://jira.company.com/browse/{}
```

## Continuous Improvement

### Analyze Test Metrics

1. **Success Rate**: Target > 95%
2. **Execution Time**: Track trends
3. **Flaky Tests**: Identify and fix
4. **Code Coverage**: Increase over time

### Regular Review

```bash
# Weekly: Review test results
# Monthly: Analyze trends, update documentation
# Quarterly: Optimize pipeline performance
```

## References

- [Jenkinsfile Documentation](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Jenkins Credentials Plugin](https://plugins.jenkins.io/credentials/)
- [Docker Networking](https://docs.docker.com/network/)
- [pytest Documentation](https://docs.pytest.org/)
- [Allure Documentation](https://docs.qameta.io/allure/)
