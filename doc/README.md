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
- pip of uv
- Digitale Coach Mock Server draaiend op `http://localhost:8000`

### Setup met pip (standaard)

```bash
# Clone of navigeer naar project
cd digitalecoach_client

# Maak virtuele omgeving
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt
```

### Setup met uv (sneller & makkelijker)

```bash
# Clone of navigeer naar project
cd digitalecoach_client

# Installeer dependencies (uv maakt automatisch venv aan)
uv sync

# Activeer omgeving
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**Voordelen van uv:**
- ⚡ 10-100x sneller dan pip
- 📦 Automatische virtual environment
- 🔒 Deterministische dependency resolution
- 🎯 Eenvoudiger dependency management

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

### Snelle Start - Scripts (Windows/macOS/Linux) ⭐ AANBEVOLEN

#### Windows (Batch Scripts)

**Tests uitvoeren (één klik):**
```bash
run_tests.bat
```

**Import uitvoeren (één klik):**
```bash
run_import.bat
```

**Import met custom files:**
```bash
run_import.bat custom_input.json custom_schema.json
```

#### macOS/Linux (Shell Scripts)

**Tests uitvoeren:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Import uitvoeren:**
```bash
chmod +x run_import.sh
./run_import.sh
```

**Import met custom files:**
```bash
./run_import.sh custom_input.json custom_schema.json
```

**Features (all platforms):**
- ✅ Controleert mock server status
- ✅ Voert alle CRUD tests uit
- ✅ Toont duidelijke succes/faal meldingen
- ✅ Gebruikt default: `procesbeschrijving\process_onboard_account.json`
- ✅ Ondersteunt custom input en schema files

### CLI Tools - Test Runner (Aanbevolen)

Voer alle tests uit met één commando:

#### Linux/macOS
```bash
# Vanuit project root
python tests/run_all_tests.py
```

#### Windows (PowerShell)
```powershell
# Vanuit project root
python tests/run_all_tests.py
```

Dit voert uit:
- ✅ Authenticatie Tests (16 tests)
- ✅ End-to-End Integratie Tests (3 tests)
- ✅ Sanering Import Tests (1 test)
- ✅ Alle logs naar `log/test/` folder
- ✅ Automatische cleanup van oude logs

**Met Debug Logging:**
```powershell
$env:DEBUG="true"; python tests/run_all_tests.py
```

**Met Checkout/Checkin (production mode):**
```powershell
$env:SKIP_CHECKOUT_CHECKIN="false"; python tests/run_all_tests.py
```

### 2. Individuele Tests

#### Test Authenticatie
```bash
python -m pytest tests/test_auth.py -v
```

#### Test End-to-End
```bash
python -m pytest tests/test_end_to_end.py -v
```

#### Test Sanering Import
```bash
python -m pytest tests/test_sanering_import.py -v
```

### 3. Import + Export Workflow

Complete workflow: importeer een proces en exporteer alle content in één keer:

#### Linux/macOS
```bash
# Vanuit project root
python main.py
```

#### Windows (PowerShell)
```powershell
# Vanuit project root
python main.py
```

**Output:**
- Export JSON: `log/export_YYYYMMDD_HHMMSS.json`
- Log file: `log/import_YYYYMMDD_HHMMSS.log`

Dit voert uit:
- ✅ Mock server reset (geen duplicate errors)
- ✅ Process laadt en valideert uit `procesbeschrijving/process_onboard_account.json`
- ✅ Topics importeert
- ✅ Alles exporteert naar JSON
- ✅ Timestamped logging in `log/` folder

**Met Debug Logging:**
```powershell
$env:DEBUG="true"; python main.py
```

**Met Checkout/Checkin (production mode):**
```powershell
$env:SKIP_CHECKOUT_CHECKIN="false"; python main.py
```

## CLI Tools

### `tests/run_all_tests.py` – Master Test Runner

Voert alle test suites uit met uitgebreide rapportage:

```bash
python tests/run_all_tests.py
```

**Tests:**
- `test_auth.py` – Authenticatie en token caching (16 tests)
- `test_end_to_end.py` – End-to-end integratie (3 tests)
- `test_sanering_import.py` – Sanering import (1 test)

**Output:**
- Log files: `log/test/pytest_YYYYMMDD_HHMMSS.log`
- JSON reports: `log/test/test_*.json`
- Real-time console output met samenvatting

### `main.py` – Import + Export Workflow

Complete workflow: importeer proces en exporteer alle content.

```bash
python main.py
```

**Voert uit:**
- Mock server reset
- Process laden en valideren uit `procesbeschrijving/process_onboard_account.json`
- Topics importeren
- Alles exporteren naar JSON

**Output:**
- Export JSON: `log/export_YYYYMMDD_HHMMSS.json`
- Log file: `log/import_YYYYMMDD_HHMMSS.log`

### Individuele Tests

**Test Authenticatie:**
```bash
python -m pytest tests/test_auth.py -v
```

**Test End-to-End:**
```bash
python -m pytest tests/test_end_to_end.py -v
```

**Test Sanering:**
```bash
python -m pytest tests/test_sanering_import.py -v
```

**Test CRUD Operaties (Volledige API Coverage):**
```bash
python -m pytest tests/test_crud_operations.py -v
```

Dit test alle 10 CRUD operaties:
- ✅ CREATE (v4) – Nieuw topic aanmaken
- ✅ READ (v1) – Topic ophalen
- ✅ READ Parts (v3) – Parts ophalen
- ✅ UPDATE Part (v2) – Part bijwerken
- ✅ UPDATE Metadata (v2) – Metadata bijwerken
- ✅ DELETE (v3) – Topic verwijderen
- ✅ CHECKOUT (v3) – Topic uitchecken
- ✅ CHECKIN (v4) – Topic inchecken
- ✅ ADD Relation (v2) – Relatie toevoegen
- ✅ ADD Tag (v2) – Tag toevoegen

## Projectstructuur

```
digitalecoach_client/
├── src/                         # Source code (organized structure)
│   ├── api_client/              # AskDelphi API client (volledige CRUD)
│   │   ├── __init__.py
│   │   ├── session.py           # Session management & API calls
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── auth.py              # Authentication & token management
│   │   ├── checkout.py          # Checkout/checkin (v3/v4)
│   │   ├── parts.py             # Parts management (v2/v3)
│   │   ├── topic.py             # Topic CRUD (v1/v2/v3)
│   │   ├── relations.py         # Relations & tags (v2)
│   │   └── project.py           # Project management
│   ├── importer/                # Import pipeline
│   │   ├── mapper.py            # JSON → Topic tree mapper
│   │   ├── importer.py          # Topic importer (volledige CRUD)
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

### Vereisten voor Tests

1. **Mockserver moet draaien** (voor test_end_to_end.py):
```bash
# In separate terminal
cd ../digitalecoach_server
uvicorn mock_server:app --reload --port 8000
```

2. **.env bestand moet ingesteld zijn** met correcte credentials:
```env
ASKDELPHI_BASE_URL=http://127.0.0.1:8000
ASKDELPHI_API_KEY=dummy-key
ASKDELPHI_TENANT=dummy-tenant
ASKDELPHI_NT_ACCOUNT=dummy-user
ASKDELPHI_ACL=Everyone
ASKDELPHI_PROJECT_ID=dummy-project
DEBUG=false
```

### Run End-to-End Tests (Aanbevolen)

**Met verbose output en korte traceback:**
```bash
python -m pytest tests/test_end_to_end.py -v --tb=short
```

**Output:**
- Toont alle test resultaten
- Korte error messages bij failures
- Timestamped log files in `log/test/` folder

**Met debug logging:**
```bash
DEBUG=true python -m pytest tests/test_end_to_end.py -v --tb=short
```

**Run specifieke test:**
```bash
python -m pytest tests/test_end_to_end.py::test_authentication_and_connection -v --tb=short
```

### Run CRUD Operatie Tests

**Volledige CRUD coverage (10 operaties) - AANBEVOLEN COMMANDO:**

Windows (PowerShell):
```powershell
cd c:\Users\arieb\CascadeProjects\digitalecoach_client; python -m pytest tests/test_crud_operations.py -v
```

Linux/macOS:
```bash
cd /path/to/digitalecoach_client && python -m pytest tests/test_crud_operations.py -v
```

**Met debug logging:**
```bash
cd c:\Users\arieb\CascadeProjects\digitalecoach_client; DEBUG=true python -m pytest tests/test_crud_operations.py -v
```

**Cascading DELETE tests:**
```bash
cd c:\Users\arieb\CascadeProjects\digitalecoach_client; python -m pytest tests/test_cascading_delete.py -v
```

### Run Alle Tests

**Master test runner (alle test suites):**
```bash
python tests/run_all_tests.py
```

### Test Resultaten

Alle tests genereren timestamped log files in `log/test/` folder:

- `pytest_YYYYMMDD_HHMMSS.log` – Pytest logs
- `test_*.json` – Test reports

### Tests Beschrijving

**test_end_to_end.py:**
- **`test_authentication_and_connection`** – Valideert authenticatie, invalid credentials, missing headers
- **`test_export_content`** – Valideert export structure, metadata, content design, topics
- **`test_import_onboard_account`** – Complete import workflow met CRUD operations

**test_crud_operations.py:**
- **`test_01_create_topic`** – CREATE (v4) operatie
- **`test_02_read_topic`** – READ (v1) operatie
- **`test_03_checkout_topic`** – CHECKOUT (v3) operatie
- **`test_04_read_parts`** – READ Parts (v3) operatie
- **`test_05_update_part`** – UPDATE Part (v2) operatie
- **`test_06_update_metadata`** – UPDATE Metadata (v2) operatie
- **`test_07_add_relation`** – ADD Relation (v2) operatie
- **`test_08_add_tag`** – ADD Tag (v2) operatie
- **`test_09_checkin_topic`** – CHECKIN (v4) operatie
- **`test_10_delete_topic`** – DELETE (v3) operatie

**test_cascading_delete.py:**
- **`test_cascading_delete_removes_children`** – Parent + children verwijderen
- **`test_cascading_delete_with_nested_hierarchy`** – Geneste hiërarchie (3 niveaus)
- **`test_cascading_delete_preserves_siblings`** – Siblings behouden

### Test Coverage

✅ **15 topics** exported met valid structure
✅ **12 topics** imported met complete CRUD workflow
✅ **41 topic types** in content design
✅ **10 CRUD operaties** getest
✅ **3 cascading delete scenarios** getest
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

**"src not module" of import errors bij testen:**

Dit probleem treedt op wanneer pytest wordt uitgevoerd van buiten de project root. 

**Oplossing:** Zorg dat je in de project root directory bent en gebruik `python -m pytest`:

```bash
# CORRECT - Vanuit project root met python -m pytest
cd c:\Users\arieb\CascadeProjects\digitalecoach_client
python -m pytest tests/test_crud_operations.py -v

# FOUT - Rechtstreeks pytest commando
pytest tests/test_crud_operations.py -v
```

Het `conftest.py` bestand in de project root zorgt ervoor dat de Python path correct wordt ingesteld.

**Module not found errors:**
```bash
# Zorg dat je in de juiste directory bent
cd digitalecoach_client
pip install -r requirements.txt

# Of zet PYTHONPATH
export PYTHONPATH=/path/to/digitalecoach_client
python -m pytest tests/test_end_to_end.py -v
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
