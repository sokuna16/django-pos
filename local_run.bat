@echo off
setlocal enabledelayedexpansion

:: Set the path to the virtual environment
set VENV_PATH=C:\Users\marin\Downloads\POS\myenv

:: Activate the virtual environment
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call "%VENV_PATH%\Scripts\activate.bat" || (
        echo Failed to activate virtual environment. Exiting.
        exit /b 1
    )
) else (
    echo Virtual environment is already activated.
)

:: Verify Python version and package installation
python --version || (
    echo Python is not installed or not accessible. Exiting.
    exit /b 1
)

:: Check if 'requests' package is installed
pip show requests >nul 2>&1 || (
    echo Installing 'requests' package...
    pip install requests
)

:: Start the Django development server
echo Starting the Django development server...
start python manage.py runserver

:: Wait to ensure the server starts
timeout /t 3 /nobreak >nul

:: Open the default web browser
start http://127.0.0.1:8000/

echo Server is running. You can access it at http://127.0.0.1:8000/

:: Prevent the script from closing immediately
pause
