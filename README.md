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
```

## Gebruik

### 1. Import + Export Workflow (Aanbevolen)

Complete workflow: importeer een proces en exporteer alle content in één keer:

```bash
python run_import_and_export.py \
  --input examples/process_onboard_account.json \
  --schema examples/process_schema.json
```

**Output:** `export/export_with_content.json`

Dit is de aanbevolen manier omdat het:
- ✅ Mock server reset (geen duplicate errors)
- ✅ Process laadt en valideert
- ✅ Topics importeert
- ✅ Alles exporteert naar JSON

### 2. Alleen Importeren

```bash
python main.py \
  --input examples/process_onboard_account.json \
  --schema examples/process_schema.json
```

Importeert een proces in AskDelphi zonder te exporteren.

### 3. Alleen Exporteren

```bash
python exporter.py --output export_latest.json
```

Exporteert alle huidige content uit AskDelphi als JSON.

## CLI Tools

### `run_import_and_export.py` – Complete Workflow

Importeert een proces en exporteert alle content.

```bash
python run_import_and_export.py \
  --input <path> \
  --schema <path> \
  [--output <path>]
```

**Opties:**
- `--input` (verplicht) – Pad naar process JSON
- `--schema` (verplicht) – Pad naar JSON schema
- `--output` (optioneel) – Output pad (default: `export/export_with_content.json`)

### `main.py` – Importer

Importeert een proces in AskDelphi.

```bash
python main.py \
  --input <path> \
  --schema <path>
```

**Opties:**
- `--input` (verplicht) – Pad naar process JSON
- `--schema` (verplicht) – Pad naar JSON schema

### `exporter.py` – Exporter

Exporteert alle content uit AskDelphi als JSON.

```bash
python exporter.py [--output <path>]
```

**Opties:**
- `--output` (optioneel) – Output pad (default: `export_YYYYMMDD_HHMMSS.json`)

## Projectstructuur

```
digitalecoach_client/
├── main.py                      # Importer CLI
├── exporter.py                  # Exporter CLI
├── run_import_and_export.py     # Combined workflow
├── askdelphi/                   # AskDelphi API client
│   ├── __init__.py
│   ├── session.py              # Session management & API calls
│   ├── exceptions.py           # Custom exceptions
│   ├── checkout.py             # Checkout/checkin operations
│   ├── parts.py                # Parts management
│   └── project.py              # Project management
├── importer/                    # Import pipeline
│   ├── mapper.py               # JSON → Topic tree mapper
│   ├── importer.py             # Topic importer
│   └── validator.py            # JSON schema validator
├── config/
│   ├── env.py                  # Environment configuration
│   └── topic_types.py          # Topic type definitions
├── examples/
│   ├── process_onboard_account.json  # Example process
│   └── process_schema.json           # JSON schema
├── export/                      # Export output folder
├── tests/                       # Test suite
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # Dit bestand
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
pytest
```

### Run specifieke test

```bash
pytest tests/test_end_to_end.py::test_export_content -v
```

### Tests beschrijving

- **`test_authentication_and_connection`** – Valideert authenticatie en verbinding
- **`test_export_content`** – Valideert export functionaliteit
- **`test_import_onboard_account`** – Valideert complete import workflow

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

## Troubleshooting

**Module not found errors:**
```bash
# Zorg dat je in de juiste directory bent
cd digitalecoach_client
pip install -r requirements.txt
```

**Connection refused:**
```bash
# Zorg dat mock server draait
cd ../digitalecoach_server
uvicorn mock_server:app --reload
```

**Topic already exists:**
```bash
# Reset mock server state
curl -X POST http://localhost:8000/reset
```

**JSON validation errors:**
```bash
# Check schema bestand
# Zorg dat --schema pad correct is
python run_import_and_export.py --input examples/process_onboard_account.json --schema examples/process_schema.json
```
