# Hoe main.py runnen?

## Mock Server (Testen)
```powershell
$env:ASKDELPHI_BASE_URL='http://127.0.0.1:8000'
$env:ASKDELPHI_API_KEY='dummy-key'
$env:ASKDELPHI_TENANT='dummy-tenant'
$env:ASKDELPHI_NT_ACCOUNT='dummy-user'
$env:ASKDELPHI_ACL='Everyone'
$env:ASKDELPHI_PROJECT_ID='dummy-project'
$env:USE_AUTH_CACHE='false'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

## Productie (Traditioneel)
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_API_KEY='your-api-key'
$env:ASKDELPHI_TENANT='your-tenant'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:ASKDELPHI_ACL='your-acl'
$env:ASKDELPHI_PROJECT_ID='your-project'
$env:USE_AUTH_CACHE='false'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

## Productie (Token Caching - Aanbevolen)
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_CMS_URL='https://company.askdelphi.com/cms/tenant/xxx/project/yyy/acl/zzz/page'
$env:ASKDELPHI_PORTAL_CODE='ABC123-XYZ789'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

## Wat gebeurt er?
- Proces wordt geladen
- Bestaand proces wordt verwijderd (cascade delete)
- Nieuw proces wordt geïmporteerd
