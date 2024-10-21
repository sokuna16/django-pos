@echo off
setlocal enabledelayedexpansion

:: Set the full path to the virtual environment
set VENV_PATH=C:\Users\marin\Downloads\POS\myenv

:: Check if the virtual environment is already activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...

    :: Activate the virtual environment using the full path
    call "%VENV_PATH%\Scripts\activate.bat" || (
        echo Failed to activate the virtual environment. Exiting.
        exit /b 1
    )
) else (
    echo Virtual environment is already activated.
)

:: Verify Python and requests package installation
python --version
pip show requests >nul 2>&1 || (
    echo Installing requests package...
    pip install requests
)

:: Get the IP address of the device
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr "IPv4"') do (
    set "IP=%%I"
)

:: Remove leading spaces from the IP address
set "IP=%IP:~1%"

:: Path to settings.py
set "file=POSwebapp\POSwebapp\settings.py"
set "temp_file=temp_settings.py"

:: Check if the IP is already in ALLOWED_HOSTS
set "ip_found=false"
for /f "usebackq tokens=* delims=" %%a in ("%file%") do (
    echo %%a | findstr /c:"'%IP%'" >nul && set "ip_found=true"
)

:: If the IP is not found, update ALLOWED_HOSTS
if "!ip_found!"=="false" (
    echo Adding %IP% to ALLOWED_HOSTS...

    (
        for /f "usebackq tokens=* delims=" %%a in ("%file%") do (
            echo %%a | findstr "ALLOWED_HOSTS" >nul && (
                echo Updating ALLOWED_HOSTS with %IP%.
                echo ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '%IP%', '0.0.0.0', '%IP%']
            ) || echo %%a
        )
    ) > "%temp_file%"

    move /Y "%temp_file%" "%file%" >nul
) else (
    echo IP %IP% is already in ALLOWED_HOSTS.
)

:: Start the Django development server
echo Starting the Django development server...
start cmd /k python manage.py runserver 0.0.0.0:8000

:: Wait to ensure the server starts
timeout /t 3 /nobreak >nul

:: Open the default web browser with the IP address
start http://%IP%:8000/

echo Server is running. You can access it at http://%IP%:8000/

:: Prevent the script from closing immediately
pause
