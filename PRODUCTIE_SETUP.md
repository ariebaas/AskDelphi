# Productie Setup Guide - Digitalecoach Client

## Overzicht

Dit document beschrijft hoe je `main.py` kunt runnen tegen:
1. **Mock Server** (voor testen/development)
2. **Productie Server** (met traditionele auth)
3. **Productie Server** (met token caching - aanbevolen)

---

## 1. Mock Server Setup (Testen)

### Wanneer gebruiken?
- Lokale development en testen
- Geen echte AskDelphi credentials nodig
- Snelle feedback loop

### Commando:
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

### Wat gebeurt er?
- Proces wordt geladen uit `process_sanering.json`
- Bestaand proces wordt verwijderd (cascade delete)
- Nieuw proces wordt geïmporteerd tegen mock server op `http://127.0.0.1:8000`

---

## 2. Productie Server - Traditionele Auth

### Wanneer gebruiken?
- Productie omgeving
- Je hebt een API key beschikbaar
- Geen token caching nodig

### Stap 1: Credentials verzamelen
Je hebt nodig:
- `ASKDELPHI_BASE_URL`: https://your-company.askdelphi.com/api
- `ASKDELPHI_API_KEY`: Je echte API sleutel
- `ASKDELPHI_TENANT`: Tenant ID
- `ASKDELPHI_NT_ACCOUNT`: Je gebruikersnaam (bijv. john.doe)
- `ASKDELPHI_ACL`: ACL ID
- `ASKDELPHI_PROJECT_ID`: Project ID

### Stap 2: Commando uitvoeren
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_API_KEY='your-actual-api-key'
$env:ASKDELPHI_TENANT='your-tenant-id'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:ASKDELPHI_ACL='your-acl-id'
$env:ASKDELPHI_PROJECT_ID='your-project-id'
$env:USE_AUTH_CACHE='false'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

### Wat gebeurt er?
- Authenticatie met API key
- Nieuw sessie token wordt opgehaald
- Proces wordt geïmporteerd

---

## 3. Productie Server - Token Caching (Aanbevolen)

### Wanneer gebruiken?
- Productie omgeving
- Betere performance (tokens worden hergebruikt)
- Automatische token vernieuwing
- Veiliger (geen API key in .env)

### Stap 1: CMS URL en Portal Code verzamelen

**CMS URL:**
1. Open AskDelphi in je browser
2. Navigeer naar een Digital Coach pagina
3. Kopieer de volledige URL uit de adresbalk
4. Format: `https://company.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ID}/...`

**Portal Code:**
1. Open AskDelphi Mobile app of web interface
2. Ga naar Settings → Mobile tab
3. Kopieer de Portal Code (format: ABC123-XYZ789)
4. **BELANGRIJK**: Dit is eenmalig gebruik! Haal een verse code op als authenticatie faalt

### Stap 2: Commando uitvoeren
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_CMS_URL='https://company.askdelphi.com/cms/tenant/abc-123/project/def-456/acl/ghi-789/page'
$env:ASKDELPHI_PORTAL_CODE='ABC123-XYZ789'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
```

### Wat gebeurt er?
- **Eerste keer**: Portal code wordt uitgewisseld voor access en refresh tokens
- **Tokens worden opgeslagen** in `.askdelphi_tokens.json`
- **Volgende keren**: Cached tokens worden hergebruikt
- **Automatisch**: Tokens worden vernieuwd 5 minuten voor expiry

### Voordelen
- ✅ Betere performance (tokens hergebruikt)
- ✅ Automatische token management
- ✅ Veiliger (geen API key nodig)
- ✅ Naadloze operatie

---

## Snelle Referentie

### Mock Server
```powershell
$env:ASKDELPHI_BASE_URL='http://127.0.0.1:8000'
$env:ASKDELPHI_API_KEY='dummy-key'
$env:ASKDELPHI_TENANT='dummy-tenant'
$env:ASKDELPHI_NT_ACCOUNT='dummy-user'
$env:ASKDELPHI_ACL='Everyone'
$env:ASKDELPHI_PROJECT_ID='dummy-project'
$env:USE_AUTH_CACHE='false'
```

### Productie (Traditioneel)
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_API_KEY='your-api-key'
$env:ASKDELPHI_TENANT='your-tenant'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:ASKDELPHI_ACL='your-acl'
$env:ASKDELPHI_PROJECT_ID='your-project'
$env:USE_AUTH_CACHE='false'
```

### Productie (Token Caching)
```powershell
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_CMS_URL='https://company.askdelphi.com/cms/tenant/xxx/project/yyy/acl/zzz/page'
$env:ASKDELPHI_PORTAL_CODE='ABC123-XYZ789'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'
```

---

## Troubleshooting

### "Geen access token beschikbaar"
- **Oorzaak**: `USE_AUTH_CACHE=true` maar geen geldige CMS URL/Portal Code
- **Oplossing**: Zet `USE_AUTH_CACHE=false` of geef geldige CMS URL en Portal Code

### "Portal code exchange failed"
- **Oorzaak**: Portal code is verlopen of al gebruikt
- **Oplossing**: Haal een verse Portal Code op uit AskDelphi Mobile tab

### "Could not parse CMS URL"
- **Oorzaak**: CMS URL format is incorrect
- **Oplossing**: Zorg dat URL bevat: `/tenant/{ID}/project/{ID}/acl/{ID}/`

### "Connection refused"
- **Oorzaak**: Server is niet bereikbaar
- **Oplossing**: Controleer `ASKDELPHI_BASE_URL` en server status

---

## Proces Verwijdering

Bij elke import:
1. Script controleert of proces al bestaat
2. Indien ja: bestaand proces EN alle child topics worden verwijderd
3. Vervolgens: nieuw proces wordt geïmporteerd

Dit zorgt voor schone imports zonder conflicten.

---

## Volgende Stappen

1. **Mock Server testen**: Volg stap 1 om te verifiëren dat alles werkt
2. **Productie voorbereiding**: Verzamel credentials van je AskDelphi admin
3. **Productie import**: Kies traditioneel of token caching en voer commando uit
4. **Verificatie**: Check logs en export JSON om te verifiëren dat alles correct is geïmporteerd
