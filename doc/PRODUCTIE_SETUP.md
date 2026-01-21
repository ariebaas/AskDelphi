# Hoe main.py runnen?

## 1. Mock Server (Testen)

Zet eerst de directory naar het project:
```
cd C:\Users\arieb\CascadeProjects\digitalecoach_client
```

Kopieer en plak dit volledige commando in PowerShell:

```
$env:ASKDELPHI_BASE_URL='http://127.0.0.1:8000'; $env:ASKDELPHI_API_KEY='dummy-key'; $env:ASKDELPHI_TENANT='dummy-tenant'; $env:ASKDELPHI_NT_ACCOUNT='dummy-user'; $env:ASKDELPHI_ACL='Everyone'; $env:ASKDELPHI_PROJECT_ID='dummy-project'; $env:USE_AUTH_CACHE='false'; python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

## 2. Productie (Traditioneel)

Zet eerst de directory naar het project:
```
cd C:\Users\arieb\CascadeProjects\digitalecoach_client
```

Vervang de waarden tussen aanhalingstekens en kopieer het volledige commando:

```
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'; $env:ASKDELPHI_API_KEY='your-api-key'; $env:ASKDELPHI_TENANT='your-tenant'; $env:ASKDELPHI_NT_ACCOUNT='your-username'; $env:ASKDELPHI_ACL='your-acl'; $env:ASKDELPHI_PROJECT_ID='your-project'; $env:USE_AUTH_CACHE='false'; python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

**Vervang deze waarden:**
- `your-company.askdelphi.com/api` → Jouw AskDelphi API URL
- `your-api-key` → Jouw API key
- `your-tenant` → Jouw tenant ID
- `your-username` → Jouw NT account/username
- `your-acl` → Jouw ACL waarde
- `your-project` → Jouw project ID

## 3. Productie (Token Caching - Aanbevolen)

Zet eerst de directory naar het project:
```
cd C:\Users\arieb\CascadeProjects\digitalecoach_client
```

Vervang de waarden en kopieer het volledige commando:

```
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'; $env:ASKDELPHI_CMS_URL='https://company.askdelphi.com/cms/tenant/xxx/project/yyy/acl/zzz/page'; $env:ASKDELPHI_PORTAL_CODE='ABC123-XYZ789'; $env:ASKDELPHI_NT_ACCOUNT='your-username'; $env:USE_AUTH_CACHE='true'; python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

**Vervang deze waarden:**
- `your-company.askdelphi.com/api` → Jouw AskDelphi API URL
- `company.askdelphi.com/cms/tenant/xxx/project/yyy/acl/zzz/page` → Jouw CMS URL
- `ABC123-XYZ789` → Jouw portal code
- `your-username` → Jouw NT account/username

## Wat gebeurt er?

1. Proces wordt geladen uit `procesbeschrijving/process_sanering.json`
2. Schema wordt gevalideerd uit `procesbeschrijving/process_schema.json`
3. Bestaand proces wordt verwijderd (cascade delete)
4. Nieuw proces wordt geïmporteerd in AskDelphi
5. Alle topics en relaties worden aangemaakt

## Troubleshooting

**"can't open file 'main.py'"**
- Zorg dat je in de juiste directory bent: `C:\Users\arieb\CascadeProjects\digitalecoach_client`

**Connection refused**
- Voor Mock Server: Zorg dat de mock server draait op `http://127.0.0.1:8000`
- Voor Productie: Controleer de ASKDELPHI_BASE_URL

**Authentication failed**
- Controleer je API key, tenant, en NT account
- Voor token caching: Controleer je CMS URL en portal code
