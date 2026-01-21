# Hoe main.py runnen?

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

## Productie (Token Caching)

Vervang de waarden en voer uit:

cd C:\Users\arieb\CascadeProjects\digitalecoach_client
$env:ASKDELPHI_BASE_URL='https://your-api-url'
$env:ASKDELPHI_CMS_URL='https://your-cms-url'
$env:ASKDELPHI_PORTAL_CODE='your-portal-code'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'
python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
