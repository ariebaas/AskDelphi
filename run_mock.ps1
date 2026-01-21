# Start mock server
Write-Host "Mock server starten..." -ForegroundColor Green
python -m pytest tests/test_sanering_import.py --tb=short

# Wacht even zodat server volledig opstart
Start-Sleep -Seconds 2

# Zet environment variables
$env:ASKDELPHI_BASE_URL='http://127.0.0.1:8000'
$env:ASKDELPHI_API_KEY='dummy-key'
$env:ASKDELPHI_TENANT='dummy-tenant'
$env:ASKDELPHI_NT_ACCOUNT='dummy-user'
$env:ASKDELPHI_ACL='Everyone'
$env:ASKDELPHI_PROJECT_ID='dummy-project'
$env:USE_AUTH_CACHE='false'

Write-Host "Proces importeren..." -ForegroundColor Green
python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
