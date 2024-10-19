@echo off

:: Check if the virtual environment is already activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call myenv\Scripts\activate
) else (
    echo Virtual environment is already activated.
)

echo Starting the Django development server...
start python manage.py runserver

:: Wait a moment to ensure the server starts
timeout /t 3 /nobreak >nul

:: Open the default web browser
start http://127.0.0.1:8000/

echo Server is running. You can access it at http://127.0.0.1:8000/
