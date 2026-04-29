# Jenkins Setup Guide

Complete guide for setting up Jenkins and configuring credentials for the PyTest DQ Framework pipeline.

## Table of Contents

- [Jenkins Installation](#jenkins-installation)
- [Initial Configuration](#initial-configuration)
- [Credentials Setup](#credentials-setup)
- [Pipeline Configuration](#pipeline-configuration)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Jenkins Installation

### Using Docker Compose

Jenkins is automatically configured in `docker-compose.yml` and starts with PostgreSQL.

```bash
# Start Jenkins and PostgreSQL
docker-compose up -d

# Verify Jenkins is running
docker ps | grep jenkins

# Check Jenkins startup logs
docker logs jenkins -f
```

### Access Jenkins

1. Open browser: `http://localhost:8080`
2. Jenkins may take 1-2 minutes to fully start

### Retrieve Initial Admin Password

#### Option 1: From File
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### Option 2: From Logs
```bash
docker logs jenkins | grep -A 5 "initialAdminPassword"
```

#### Option 3: Direct File Path
If running locally:
```bash
cat jenkins_home/secrets/initialAdminPassword
```

## Initial Configuration

### First Login

1. Navigate to `http://localhost:8080`
2. Paste the initial admin password
3. Click **Continue**

### Install Suggested Plugins

1. Click **Install suggested plugins**
2. Wait for installation to complete (5-10 minutes)
3. Create first admin user:
   - Username: `admin`
   - Password: Use a strong password
   - Full name: `Administrator`
   - Email: Your email address
4. Click **Save and Continue**

### Install Additional Plugins (Optional)

Recommended plugins:
- **GitHub Integration** (if using GitHub SCM)
- **Pipeline: GitHub Groovy Libraries** (for Jenkinsfile)
- **Cobertura Plugin** (for coverage reports)
- **Allure Plugin** (for Allure report integration)
- **HTML Publisher Plugin** (already included)

To install:
1. Go to **Manage Jenkins** → **Manage Plugins**
2. Go to **Available** tab
3. Search for plugin name
4. Check the checkbox
5. Click **Install without restart** or **Download now and install after restart**

## Credentials Setup

### Create PostgreSQL Credentials

#### Step 1: Navigate to Credentials Page

1. Click **Manage Jenkins** in left sidebar
2. Click **Manage Credentials**
3. Click **Global** under "Stores scoped to Jenkins"
4. Click **Add Credentials** button

#### Step 2: Create Username and Password Credential

Fill in the following:

```
Kind:              Username with password
Scope:             Global
Username:          myuser
Password:          mypassword
ID:                POSTGRES_SECRET  (IMPORTANT - must match Jenkinsfile)
Description:       PostgreSQL database credentials
```

**Important:** The `ID` field must be exactly `POSTGRES_SECRET` to match the Jenkinsfile:

```groovy
environment {
    POSTGRES_CREDENTIALS = credentials('POSTGRES_SECRET')
    DB_USER = "${POSTGRES_CREDENTIALS_USR}"
    DB_PASSWORD = "${POSTGRES_CREDENTIALS_PSW}"
}
```

#### Step 3: Verify Credential

1. Return to Credentials page
2. You should see `POSTGRES_SECRET` listed under Global credentials

### Create GitHub Credentials (Optional)

If using GitHub:

1. **Generate GitHub Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Click **Generate new token**
   - Select scopes: `repo`, `admin:repo_hook`
   - Copy token

2. **Add to Jenkins**
   - Navigate to **Manage Jenkins** → **Manage Credentials**
   - Click **Global** → **Add Credentials**
   - Kind: `Username with password`
   - Username: Your GitHub username
   - Password: Your GitHub token
   - ID: `GITHUB_CREDENTIALS`
   - Click **Create**

## Pipeline Configuration

### Create Pipeline Job

#### Step 1: Create New Job

1. Click **New Item** in Jenkins home
2. Enter job name (e.g., `DQ_Tests_Pipeline`)
3. Select **Pipeline**
4. Click **OK**

#### Step 2: Configure Git Repository

Under **Pipeline** section, select **Pipeline script from SCM**:

```
SCM:                    Git
Repository URL:         https://github.com/your-username/your-repo.git
Credentials:            GITHUB_CREDENTIALS (if private repo)
Branch Specifier:       */main
Script Path:            PyTest DQ Framework/Jenkinsfile
```

#### Step 3: Build Triggers (Optional)

Configure when pipeline should run:

- **GitHub hook trigger**: Runs on push to GitHub
- **Poll SCM**: Runs on schedule
  ```
  H H(0-23) * * *  (Run once per day at random time)
  H H * * 1-5      (Run once per weekday at random time)
  ```

#### Step 4: Save Configuration

Click **Save**

### Jenkinsfile Overview

The pipeline in `PyTest DQ Framework/Jenkinsfile` includes:

```groovy
pipeline {
    agent any

    environment {
        POSTGRES_CREDENTIALS = credentials('POSTGRES_SECRET')
        DB_HOST = 'postgres'
        DB_PORT = '5432'
        DB_NAME = 'mydatabase'
        DB_USER = "${POSTGRES_CREDENTIALS_USR}"
        DB_PASSWORD = "${POSTGRES_CREDENTIALS_PSW}"
    }

    stages {
        stage('Checkout') { ... }
        stage('Install Dependencies') { ... }
        stage('Run Tests') { ... }
        stage('Archive Reports') { ... }
        stage('Publish HTML Report') { ... }
    }
}
```

**Key points:**
- `POSTGRES_CREDENTIALS = credentials('POSTGRES_SECRET')` - references the credential created above
- `DB_HOST = 'postgres'` - uses Docker network (not localhost)
- Jenkins container can access PostgreSQL container via hostname `postgres`

## Environment Variables

### Available in Jenkinsfile

The following environment variables are set automatically:

```groovy
POSTGRES_CREDENTIALS_USR  # Username extracted from POSTGRES_SECRET
POSTGRES_CREDENTIALS_PSW  # Password extracted from POSTGRES_SECRET
DB_HOST                   # PostgreSQL host in Docker network
DB_PORT                   # PostgreSQL port
DB_NAME                   # Database name
DB_USER                   # Database user
DB_PASSWORD               # Database password
```

### Setting Custom Environment Variables

In Jenkins UI:

1. Go to job configuration
2. Under **Build Environment**, check **Use secret text(s) or files(s)**
3. Add bindings for additional secrets

Or in Jenkinsfile:

```groovy
environment {
    CUSTOM_VAR = 'value'
    TIMEOUT_SECONDS = '300'
    REPORT_FORMAT = 'html'
}
```

### Using Environment Variables in Pipeline

```groovy
stage('Run Tests') {
    steps {
        sh '''
            pytest tests \
                --db_host=${DB_HOST} \
                --db_port=${DB_PORT} \
                --db_user=${DB_USER} \
                --db_password=${DB_PASSWORD} \
                --db_name=${DB_NAME}
        '''
    }
}
```

## Running the Pipeline

### Manual Trigger

1. Open job in Jenkins
2. Click **Build Now**
3. Monitor build in **Build History**
4. Click on build number to view logs

### View Build Logs

1. Click on build number (e.g., `#1`)
2. Click **Console Output** to see real-time logs
3. Or use Jenkins API:
   ```bash
   curl http://localhost:8080/jenkins/job/DQ_Tests_Pipeline/lastBuild/consoleText
   ```

### View Test Report

After build completes:

1. Click on build
2. Click **PyTest DQ Report** (HTML report)
3. Or in job page, click **HTML Report** in left sidebar

## Jenkins Network Configuration

### Docker Network Connection

Jenkins container connects to PostgreSQL via Docker network:

```
Jenkins (localhost:8080) → Docker Network (tafordqenetwork)
                        ↓
                  PostgreSQL (postgres:5432)
```

**Important:** Use `postgres` as hostname inside containers, `localhost:5434` from host.

### Port Mapping

| Service | Container Port | Host Port | Access From |
|---------|----------------|-----------|-------------|
| Jenkins | 8080 | 8080 | http://localhost:8080 |
| Jenkins Agent | 50000 | 50000 | Internal |
| PostgreSQL | 5432 | 5434 | localhost:5434 |

## Credential Management

### Update Credentials

1. **Manage Jenkins** → **Manage Credentials**
2. Click **Global**
3. Find credential → Click on it
4. Click **Update**
5. Modify fields
6. Click **Save**

### Delete Credentials

1. **Manage Jenkins** → **Manage Credentials**
2. Click **Global**
3. Find credential → Click X icon
4. Click **Yes** to confirm

### Rotate Credentials

When changing database password:

1. Update password in `docker-compose.yml`
2. Update PostgreSQL container with new password
3. Update `POSTGRES_SECRET` credential in Jenkins
4. Rebuild pipeline

## Backup and Recovery

### Backup Jenkins Configuration

```bash
# Backup entire Jenkins home directory
docker cp jenkins:/var/jenkins_home ./jenkins_backup_$(date +%Y%m%d)

# Or with Docker volume
docker run --rm -v jenkins_home:/jenkins -v $(pwd):/backup \
  ubuntu tar czf /backup/jenkins_backup.tar.gz -C / jenkins
```

### Restore Jenkins Configuration

```bash
# From backup directory
docker cp ./jenkins_backup /jenkins:/var/jenkins_home

# Restart Jenkins
docker-compose restart jenkins
```

## Troubleshooting

### Issue: "Connection refused to PostgreSQL"

**Cause:** Hostname mismatch

**Solution:**
```groovy
// In Jenkinsfile
environment {
    DB_HOST = 'postgres'  // NOT 'localhost'
}
```

### Issue: "POSTGRES_SECRET not found"

**Cause:** Credential ID mismatch

**Solution:**
1. Verify credential ID is exactly `POSTGRES_SECRET`
2. Check spelling in Jenkinsfile
3. Recreate credential if needed

### Issue: "Jenkins can't access repository"

**Cause:** Missing GitHub credentials

**Solution:**
1. Create GitHub credential in Jenkins
2. Configure repository with credential
3. Test connection: **Pipeline Syntax** → **Checkout** → **Generate**

### Issue: "Tests timeout in Jenkins"

**Cause:** Pipeline execution limit

**Solution:**
```groovy
options {
    timeout(time: 1, unit: 'HOURS')
}
```

### Issue: "HTML report not generated"

**Cause:** pytest-html not installed or path incorrect

**Solution:**
```groovy
stage('Run Tests') {
    steps {
        sh '''
            # Verify pytest-html is installed
            pip list | grep pytest-html
            
            # Run with explicit report path
            pytest tests --html=report.html --self-contained-html
        '''
    }
}
```

### Issue: "Can't view Jenkins UI"

**Check service status:**
```bash
docker ps | grep jenkins
docker logs jenkins

# If not running
docker-compose up -d jenkins
```

**Clear browser cache:**
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

## Security Best Practices

### 1. Secure Credentials

- ✅ Use Jenkins credentials system
- ✅ Rotate passwords regularly
- ❌ Don't hardcode passwords in Jenkinsfile
- ❌ Don't log credentials

### 2. Enable Security

1. **Manage Jenkins** → **Configure Global Security**
2. Enable **Security Realm**: Local user database
3. Enable **Authorization Strategy**: Project-based
4. Enable CSRF protection

### 3. Configure User Permissions

1. **Manage Jenkins** → **Manage and Assign Roles**
2. Create roles with specific permissions
3. Assign users to roles

### 4. Use GitHub OAuth (Optional)

1. Create GitHub OAuth app
2. Configure in Jenkins
3. Users can login with GitHub

## References

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Jenkins Credentials Plugin](https://plugins.jenkins.io/credentials/)
- [Jenkinsfile Documentation](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Docker Networking](https://docs.docker.com/network/)
