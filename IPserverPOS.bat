@echo off
setlocal enabledelayedexpansion

:: Check if the virtual environment is already activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call myenv\Scripts\activate
) else (
    echo Virtual environment is already activated.
)

:: Get the IP address of the device
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr "IPv4"') do (
    set "IP=%%I"
)

:: Remove leading spaces from the IP address
set "IP=%IP:~1%"

:: Path to settings.py
set "file=settings.py"
set "temp_file=temp_settings.py"

:: Initialize a flag to track if the IP is already present
set "ip_found=false"

:: Check if the IP is already in ALLOWED_HOSTS
for /f "usebackq tokens=* delims=" %%a in ("!file!") do (
    echo %%a | findstr /c:"'%IP%'" >nul && set "ip_found=true"
)

:: If the IP is not found, update ALLOWED_HOSTS
if "!ip_found!"=="false" (
    echo Adding %IP% to ALLOWED_HOSTS...

    (
        for /f "usebackq tokens=* delims=" %%a in ("!file!") do (
            echo %%a | findstr "ALLOWED_HOSTS" >nul && (
                echo Updating ALLOWED_HOSTS with %IP%.
                echo ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '%IP%', '0.0.0.0']
            ) || echo %%a
        )
    ) > "!temp_file!"

    :: Replace the original settings.py with the updated one
    move /Y "!temp_file!" "!file!" >nul
) else (
    echo IP %IP% is already in ALLOWED_HOSTS.
)

:: Start the Django development server
echo Starting the Django development server...
start python manage.py runserver 0.0.0.0:8000

:: Wait a moment to ensure the server starts
timeout /t 3 /nobreak >nul

:: Open the default web browser with the device's IP address
start http://%IP%:8000/

echo Server is running. You can access it at http://%IP%:8000/

:: Prevent the script from closing immediately
pause
