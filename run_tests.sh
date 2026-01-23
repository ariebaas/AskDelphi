#!/bin/bash
# Test runner script for digitalecoach_client CRUD tests
# Usage: ./run_tests.sh

set -e

cd "$(dirname "$0")"

echo ""
echo "============================================================================"
echo " DIGITALE COACH - CRUD TESTS"
echo "============================================================================"
echo ""

# Check if mock server is running
echo "Checking mock server status..."
if ! curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    echo ""
    echo "WARNING: Mock server does not appear to be running on http://127.0.0.1:8000"
    echo "Start the mock server first:"
    echo "  cd ../digitalecoach_server"
    echo "  uvicorn mock_server:app --host 127.0.0.1 --port 8000"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo ""
echo "Running CRUD tests..."
echo ""

if python -m pytest tests/test_crud_operations.py -v; then
    echo ""
    echo "============================================================================"
    echo " TESTS PASSED"
    echo "============================================================================"
    echo ""
    exit 0
else
    echo ""
    echo "============================================================================"
    echo " TESTS FAILED"
    echo "============================================================================"
    echo ""
    exit 1
fi
