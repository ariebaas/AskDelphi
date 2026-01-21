# Digitale Coach Client

Client applicatie voor het importeren en exporteren van processen naar/van AskDelphi (of de mock server).

## 📋 Inhoud

- [Installatie](#installatie)
- [Configuratie](#configuratie)
- [Gebruik](#gebruik)
- [CLI Tools](#cli-tools)
- [Projectstructuur](#projectstructuur)
- [Workflow Details](#workflow-details)
- [Testen](#testen)
- [Environment Variabelen](#environment-variabelen)

## Installatie

### Vereisten
- Python 3.8+
- pip
- Digitale Coach Mock Server draaiend op `http://localhost:8000`

### Setup

```bash
# Clone of navigeer naar project
cd digitalecoach_client

# Maak virtuele omgeving
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt
```

## Configuratie

Maak een `.env` bestand in de project root:

```env
ASKDELPHI_BASE_URL=http://localhost:8000
ASKDELPHI_API_KEY=dummy-key
ASKDELPHI_TENANT=dummy-tenant
ASKDELPHI_NT_ACCOUNT=dummy-user
ASKDELPHI_ACL=Everyone
ASKDELPHI_PROJECT_ID=dummy-project
DEBUG=false
SKIP_CHECKOUT_CHECKIN=true
```

### Environment Variabelen

| Variabele | Default | Beschrijving |
|-----------|---------|-------------|
| `ASKDELPHI_BASE_URL` | - | Base URL van AskDelphi API (bijv. http://localhost:8000) |
| `ASKDELPHI_API_KEY` | - | API key voor authenticatie |
| `ASKDELPHI_TENANT` | - | Tenant ID |
| `ASKDELPHI_NT_ACCOUNT` | - | NT account naam |
| `ASKDELPHI_ACL` | - | Access Control List (komma-gescheiden) |
| `ASKDELPHI_PROJECT_ID` | - | Project ID |
| `DEBUG` | `false` | Verbose logging (true/false) |
| `SKIP_CHECKOUT_CHECKIN` | `true` | Skip checkout/checkin workflow (true/false) |

**SKIP_CHECKOUT_CHECKIN:**
- `true` (default): Sneller, geen checkout/checkin calls (3x sneller)
- `false`: Met checkout/checkin workflow (production-compatible)

## Gebruik

### 1. End-to-End Tests (Aanbevolen)

Complete test suite met logging:

#### Linux/macOS
```bash
# Vanuit project root
python tests/test_end_to_end.py
```

#### Windows (PowerShell)
```powershell
# Zorg dat mock server draait (in ander PowerShell venster)
# cd ..\digitalecoach_server
# .\venv\Scripts\Activate.ps1
# uvicorn mock_server:app --reload --port 8000

# In client directory
python tests/test_end_to_end.py
```

Dit voert uit:
- ✅ Authentication tests (4 tests)
- ✅ Export content test (15 topics)
- ✅ Import workflow test (12 topics + CRUD operations)
- ✅ Alle logs naar `tests/e2e_test_YYYYMMDD_HHMMSS.log`

**Met Debug Logging:**
```powershell
$env:DEBUG="true"; python tests/test_end_to_end.py
```

**Met Checkout/Checkin (production mode):**
```powershell
$env:SKIP_CHECKOUT_CHECKIN="false"; python tests/test_end_to_end.py
```

### 2. Import + Export Workflow

Complete workflow: importeer een proces en exporteer alle content in één keer:

#### Linux/macOS
```bash
cd tests
python run_import_and_export.py \
  --input ../examples/process_onboard_account.json \
  --schema ../config/schema.json
```

#### Windows (PowerShell)
```powershell
cd tests
python run_import_and_export.py `
  --input ../examples/process_onboard_account.json `
  --schema ../config/schema.json
```

**Output:**
- Export JSON: `export_with_content_YYYYMMDD_HHMMSS.json`
- Log file: `import_export_YYYYMMDD_HHMMSS.log`

Dit is de aanbevolen manier omdat het:
- ✅ Mock server reset (geen duplicate errors)
- ✅ Process laadt en valideert
- ✅ Topics importeert
- ✅ Alles exporteert naar JSON
- ✅ Timestamped logging

### 3. Alleen Exporteren

#### Linux/macOS
```bash
cd tests
python exporter.py
```

#### Windows (PowerShell)
```powershell
cd tests
python exporter.py
```

**Output:**
- Export JSON: `export_YYYYMMDD_HHMMSS.json`
- Log file: `export_YYYYMMDD_HHMMSS.log`

Exporteert alle huidige content uit AskDelphi als JSON.

## CLI Tools

### `tests/test_end_to_end.py` – End-to-End Tests

Complete test suite met alle functionaliteit:

```bash
python tests/test_end_to_end.py
```

**Tests:**
- `test_authentication_and_connection()` – Auth flow, invalid credentials, missing headers
- `test_export_content()` – Export structure, metadata, content design
- `test_import_onboard_account()` – Complete import workflow met CRUD operations

**Output:**
- Log file: `tests/e2e_test_YYYYMMDD_HHMMSS.log`
- Real-time console output

### `tests/run_import_and_export.py` – Complete Workflow

Importeert een proces en exporteert alle content.

```bash
cd tests
python run_import_and_export.py \
  --input ../examples/process_onboard_account.json \
  --schema ../config/schema.json \
  [--output <path>]
```

**Opties:**
- `--input` (verplicht) – Pad naar process JSON
- `--schema` (verplicht) – Pad naar JSON schema
- `--output` (optioneel) – Output pad (default: `export_with_content_YYYYMMDD_HHMMSS.json`)

**Output:**
- Export JSON: `export_with_content_YYYYMMDD_HHMMSS.json`
- Log file: `import_export_YYYYMMDD_HHMMSS.log`

### `tests/exporter.py` – Exporter

Exporteert alle content uit AskDelphi als JSON.

```bash
cd tests
python exporter.py [--output <path>]
```

**Opties:**
- `--output` (optioneel) – Output pad (default: `export_YYYYMMDD_HHMMSS.json`)

**Output:**
- Export JSON: `export_YYYYMMDD_HHMMSS.json`
- Log file: `export_YYYYMMDD_HHMMSS.log`

## Projectstructuur

```
digitalecoach_client/
├── src/                         # Source code (organized structure)
│   ├── api_client/              # AskDelphi API client
│   │   ├── __init__.py
│   │   ├── session.py           # Session management & API calls
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── auth.py              # Authentication & token management
│   │   ├── checkout.py          # Checkout/checkin operations
│   │   ├── parts.py             # Parts management
│   │   └── project.py           # Project management
│   ├── importer/                # Import pipeline
│   │   ├── mapper.py            # JSON → Topic tree mapper
│   │   ├── importer.py          # Topic importer
│   │   └── validator.py         # JSON schema validator
│   └── config/
│       ├── env.py               # Environment configuration
│       └── topic_types.py       # Topic type definitions
├── tests/                       # Test suite & CLI tools
│   ├── test_auth.py             # Authentication tests
│   ├── test_end_to_end.py       # Complete e2e tests
│   ├── test_sanering_import.py  # Sanering import tests
│   ├── exporter.py              # Export utility
│   ├── run_import_and_export.py # Import + export workflow
│   ├── conftest.py              # Pytest configuration
│   └── *.log                    # Timestamped test logs
├── log/                         # Log files
│   ├── import_*.log             # main.py import logs
│   ├── export_*.json            # main.py export results
│   └── test/                    # Test-specific logs
│       ├── pytest_*.log         # Pytest logs
│       ├── sanering_test_*.log  # Sanering test logs
│       └── export_*.json        # Test export results
├── procesbeschrijving/          # Process definitions
│   ├── process_sanering.json    # Sanering process
│   └── process_schema.json      # Process schema
├── archief/                     # Archive folder
├── doc/
│   ├── API_COMPLIANCE.md        # API compliance report
│   ├── DOCUMENTATION.md         # Complete documentation
│   ├── PRODUCTIE_SETUP.md       # Production setup instructions
│   └── README.md                # Dit bestand
├── main.py                      # Main import script
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

## Workflow Details

### Import + Export Workflow

**Stap 1: Reset mockserver**
- Wist alle vorige data
- Voorkomt "Topic already exists" errors

**Stap 2: Load & Validate**
- Laadt process JSON
- Valideert tegen JSON schema

**Stap 3: Map to Topics**
- Converteert process JSON naar topic tree
- Resolveert topic types

**Stap 4: Import**
- Maakt topics aan in AskDelphi
- Handelt hiërarchie en relaties af

**Stap 5: Export**
- Haalt alle topics op
- Exporteert naar JSON bestand

### Topic Hierarchy

```
Process (Digitale Coach Homepagina)
├── Task (Digitale Coach Procespagina)
│   ├── Step (Digitale Coach Stap)
│   │   └── Instruction (Digitale Coach Instructie)
```

### Export Format

Export bestand bevat:
- **Metadata** – Versie, timestamp, topic count
- **Content Design** – Topic types, relations, tags
- **Topics** – Alle topics met parts en relations

Voorbeeld:
```json
{
  "_metadata": {
    "version": "1.0",
    "exported_at": "2026-01-20T20:15:00Z",
    "topic_count": 15,
    "source": "digitalecoach-mock-server"
  },
  "content_design": {
    "topic_types": [...],
    "relations": [],
    "tag_hierarchies": []
  },
  "topics": {
    "topic-id": {
      "id": "topic-id",
      "title": "Topic Title",
      "topic_type_id": "type-uuid",
      "parts": {...},
      "relations": {...}
    }
  }
}
```

## Testen

### Run alle tests

```bash
# Direct runnen (aanbevolen)
python tests/test_end_to_end.py

# Of met pytest
pytest tests/test_end_to_end.py -v
```

### Run specifieke test

```bash
pytest tests/test_end_to_end.py::test_export_content -v -s
```

### Test Resultaten

Alle tests genereren timestamped log files in `tests/` folder:

- `e2e_test_YYYYMMDD_HHMMSS.log` – E2E test logs
- `export_YYYYMMDD_HHMMSS.log` – Export operation logs
- `import_export_YYYYMMDD_HHMMSS.log` – Import/export workflow logs

### Tests Beschrijving

- **`test_authentication_and_connection`** – Valideert authenticatie, invalid credentials, missing headers
- **`test_export_content`** – Valideert export structure, metadata, content design, topics
- **`test_import_onboard_account`** – Complete import workflow met CRUD operations:
  - Parts management (create, update, delete)
  - Topic updates (checkout/checkin)
  - Project management (create, delete)

### Test Coverage

✅ **15 topics** exported met valid structure
✅ **12 topics** imported met complete CRUD workflow
✅ **41 topic types** in content design
✅ **100% API compliance** met AskDelphi Swagger API

## Environment Variabelen

| Variabele | Beschrijving | Default |
|-----------|-------------|---------|
| `ASKDELPHI_BASE_URL` | AskDelphi API base URL | `http://localhost:8000` |
| `ASKDELPHI_API_KEY` | API key voor authenticatie | - |
| `ASKDELPHI_TENANT` | Tenant ID | - |
| `ASKDELPHI_NT_ACCOUNT` | NT account naam | - |
| `ASKDELPHI_ACL` | ACL entry (comma-separated) | - |
| `ASKDELPHI_PROJECT_ID` | Project ID | - |
| `DEBUG` | Debug logging enabled | `false` |

## Documentatie

Voor gedetailleerde documentatie, zie:

- **[API_COMPLIANCE.md](API_COMPLIANCE.md)** – Gedetailleerde API compliance report met AskDelphi Swagger API
- **[DOCUMENTATION.md](DOCUMENTATION.md)** – Complete client documentatie met architectuur en workflows
- **[../digitalecoach_server/IMPLEMENTATION_NOTES.md](../digitalecoach_server/IMPLEMENTATION_NOTES.md)** – Server implementatie details

## Troubleshooting

**Module not found errors:**
```bash
# Zorg dat je in de juiste directory bent
cd digitalecoach_client
pip install -r requirements.txt

# Of zet PYTHONPATH
export PYTHONPATH=/path/to/digitalecoach_client
python tests/test_end_to_end.py
```

**Connection refused:**
```bash
# Zorg dat mock server draait
cd ../digitalecoach_server
uvicorn mock_server:app --reload --port 8000

# Check of server draait
curl http://127.0.0.1:8000/docs
```

**Topic already exists:**
```bash
# Reset mock server state
curl -X POST http://127.0.0.1:8000/reset

# Of via test script
python tests/test_end_to_end.py  # Automatisch reset
```

**JSON validation errors:**
```bash
# Check schema bestand
# Zorg dat --schema pad correct is
cd tests
python run_import_and_export.py \
  --input ../examples/process_onboard_account.json \
  --schema ../config/schema.json
```

**Lege log files:**
```bash
# Zorg dat mock server draait
# Log files worden gegenereerd met FlushFileHandler
# Check tests/ folder voor *.log files
ls -la tests/*.log
```

## Support

Voor vragen of issues:
1. Check DOCUMENTATION.md voor gedetailleerde info
2. Check API_COMPLIANCE.md voor API details
3. Review log files in tests/ folder
4. Run tests met `-v` flag voor verbose output
