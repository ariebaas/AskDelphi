@echo off
REM Import runner script voor digitalecoach_client
REM Gebruik: run_import.bat [input_file] [schema_file]

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================================
echo  DIGITALE COACH - IMPORT
echo ============================================================================
echo.

REM Controleer of mock server draait
echo Checking mock server status...
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:8000/docs >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Mock server is niet bereikbaar op http://127.0.0.1:8000
    echo Start de mock server eerst:
    echo   cd ..\digitalecoach_server
    echo   uvicorn mock_server:app --host 127.0.0.1 --port 8000
    echo.
    pause
    exit /b 1
)

REM Bepaal input file
if "%~1"=="" (
    set "INPUT_FILE=procesbeschrijving\process_onboard_account.json"
) else (
    set "INPUT_FILE=%~1"
)

REM Bepaal schema file
if "%~2"=="" (
    set "SCHEMA_FILE=procesbeschrijving\process_schema.json"
) else (
    set "SCHEMA_FILE=%~2"
)

REM Controleer of input file bestaat
if not exist "!INPUT_FILE!" (
    echo.
    echo ERROR: Input file niet gevonden: !INPUT_FILE!
    echo.
    echo Gebruik: run_import.bat [input_file] [schema_file]
    echo Voorbeeld: run_import.bat examples\process_onboard_account.json config\schema.json
    echo.
    pause
    exit /b 1
)

echo Input file: !INPUT_FILE!
echo Schema file: !SCHEMA_FILE!
echo.
echo Running import...
echo.

python main.py --input "!INPUT_FILE!" --schema "!SCHEMA_FILE!"

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo  IMPORT MISLUKT
    echo ============================================================================
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================================
    echo  IMPORT GESLAAGD
    echo ============================================================================
    echo.
    pause
    exit /b 0
)
