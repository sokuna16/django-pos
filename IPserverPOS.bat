@echo off

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

:: Update settings.py to include the device's IP address in ALLOWED_HOSTS
setlocal enabledelayedexpansion
set "file=settings.py"
set "temp_file=temp_settings.py"

:: Create a temporary file with the updated ALLOWED_HOSTS
(
    for /f "usebackq delims=" %%a in ("!file!") do (
        echo %%a
        echo %%a | findstr "ALLOWED_HOSTS" >nul && (
            echo ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '!IP!', '0.0.0.0']
        )
    )
) > "!temp_file!"

:: Replace the old settings.py with the new one
move /Y "!temp_file!" "!file!" >nul

echo Starting the Django development server...
start python manage.py runserver 0.0.0.0:8000

:: Wait a moment to ensure the server starts
timeout /t 3 /nobreak >nul

:: Open the default web browser with the device's IP address
start http://%IP%:8000/

echo Server is running. You can access it at http://%IP%:8000/
