@echo off
REM Windows Development Environment Setup Script
REM This script sets up the Python virtual environment and installs dependencies

setlocal enabledelayedexpansion

echo ========== PyTest DQ Framework - Windows Setup ==========
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist "venv_3.13" (
    python -m venv venv_3.13
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv_3.13\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo.
echo [3/4] Installing dependencies...
cd "PyTest DQ Framework"
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
cd ..

echo.
echo [4/4] Verifying installation...
python -c "import pytest; import pandas; import psycopg2" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Verification failed
    exit /b 1
)

echo.
echo ========== Setup Complete ==========
echo.
echo Next steps:
echo 1. Start containers: docker-compose up -d
echo 2. Run tests: cd "PyTest DQ Framework" ^& pytest tests --db_host=localhost --db_user=myuser --db_password=mypassword --db_name=mydatabase
echo 3. View report: html_report/report.html
echo.
echo To deactivate virtual environment: deactivate
pause
