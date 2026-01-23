#!/bin/bash
# Import runner script for digitalecoach_client
# Usage: ./run_import.sh [input_file] [schema_file]

set -e

cd "$(dirname "$0")"

echo ""
echo "============================================================================"
echo " DIGITALE COACH - IMPORT"
echo "============================================================================"
echo ""

# Check if mock server is running
echo "Checking mock server status..."
if ! curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    echo ""
    echo "ERROR: Mock server is not reachable on http://127.0.0.1:8000"
    echo "Start the mock server first:"
    echo "  cd ../digitalecoach_server"
    echo "  uvicorn mock_server:app --host 127.0.0.1 --port 8000"
    echo ""
    exit 1
fi

# Determine input file
if [ -z "$1" ]; then
    INPUT_FILE="procesbeschrijving/process_onboard_account.json"
else
    INPUT_FILE="$1"
fi

# Determine schema file
if [ -z "$2" ]; then
    SCHEMA_FILE="procesbeschrijving/process_schema.json"
else
    SCHEMA_FILE="$2"
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo ""
    echo "ERROR: Input file not found: $INPUT_FILE"
    echo ""
    echo "Usage: ./run_import.sh [input_file] [schema_file]"
    echo "Example: ./run_import.sh procesbeschrijving/process_onboard_account.json procesbeschrijving/process_schema.json"
    echo ""
    exit 1
fi

echo "Input file: $INPUT_FILE"
echo "Schema file: $SCHEMA_FILE"
echo ""
echo "Running import..."
echo ""

if python main.py --input "$INPUT_FILE" --schema "$SCHEMA_FILE"; then
    echo ""
    echo "============================================================================"
    echo " IMPORT SUCCEEDED"
    echo "============================================================================"
    echo ""
    exit 0
else
    echo ""
    echo "============================================================================"
    echo " IMPORT FAILED"
    echo "============================================================================"
    echo ""
    exit 1
fi
