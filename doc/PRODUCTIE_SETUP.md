# Hoe main.py runnen?

## Projectstructuur

De client code is georganiseerd in een `src/` folder:
- `src/api_client/` – AskDelphi API client
- `src/importer/` – Import pipeline
- `src/config/` – Configuration

Logs worden opgeslagen in:
- `log/import_*.log` – main.py import logs
- `log/export_*.json` – main.py export results
- `log/test/pytest_*.log` – Test logs
- `log/test/sanering_test_*.log` – Sanering test logs

## Mock Server (Testen)

Open PowerShell en voer dit uit:

cd C:\Users\arieb\CascadeProjects\digitalecoach_client
$env:ASKDELPHI_BASE_URL='http://127.0.0.1:8000'
$env:ASKDELPHI_API_KEY='dummy-key'
$env:ASKDELPHI_TENANT='dummy-tenant'
$env:ASKDELPHI_NT_ACCOUNT='dummy-user'
$env:ASKDELPHI_ACL='Everyone'
$env:ASKDELPHI_PROJECT_ID='dummy-project'
$env:USE_AUTH_CACHE='false'
python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json

Output:
- Log: log/import_YYYYMMDD_HHMMSS.log
- Export: log/export_YYYYMMDD_HHMMSS.json

## Productie (Traditioneel)

Vervang de waarden en voer uit:

cd C:\Users\arieb\CascadeProjects\digitalecoach_client
$env:ASKDELPHI_BASE_URL='https://your-api-url'
$env:ASKDELPHI_API_KEY='your-api-key'
$env:ASKDELPHI_TENANT='your-tenant'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:ASKDELPHI_ACL='your-acl'
$env:ASKDELPHI_PROJECT_ID='your-project'
$env:USE_AUTH_CACHE='false'
python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json

Output:
- Log: log/import_YYYYMMDD_HHMMSS.log
- Export: log/export_YYYYMMDD_HHMMSS.json

## Productie (Token Caching)

Vervang de waarden en voer uit:

cd C:\Users\arieb\CascadeProjects\digitalecoach_client
$env:ASKDELPHI_BASE_URL='https://your-api-url'
$env:ASKDELPHI_CMS_URL='https://your-cms-url'
$env:ASKDELPHI_PORTAL_CODE='your-portal-code'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'
python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json

Output:
- Log: log/import_YYYYMMDD_HHMMSS.log
- Export: log/export_YYYYMMDD_HHMMSS.json

## Tests runnen

Alle tests (20 tests):
python -m pytest tests/ -v

Output:
- Logs: log/test/pytest_YYYYMMDD_HHMMSS.log
- Sanering test logs: log/test/sanering_test_YYYYMMDD_HHMMSS.log
