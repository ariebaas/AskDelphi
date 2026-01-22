@echo off
REM Test runner script voor digitalecoach_client CRUD tests
REM Gebruik: run_tests.bat

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================================
echo  DIGITALE COACH - CRUD TESTS
echo ============================================================================
echo.

REM Controleer of mock server draait
echo Checking mock server status...
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:8000/docs >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Mock server lijkt niet te draaien op http://127.0.0.1:8000
    echo Start de mock server eerst:
    echo   cd ..\digitalecoach_server
    echo   uvicorn mock_server:app --host 127.0.0.1 --port 8000
    echo.
    pause
)

echo.
echo Running CRUD tests...
echo.

python -m pytest tests/test_crud_operations.py -v

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo  TESTS MISLUKT
    echo ============================================================================
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================================
    echo  TESTS GESLAAGD
    echo ============================================================================
    echo.
    pause
    exit /b 0
)
