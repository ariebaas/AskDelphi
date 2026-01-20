<<<<<<< HEAD
# AskDelphi
=======
# Digitale Coach Client

Client applicatie voor het importeren en exporteren van processen naar/van AskDelphi.

## Installatie

```bash
pip install -r requirements.txt
```

## Configuratie

Maak een `.env` bestand:

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

### 1. Import + Export Workflow

Complete workflow: importeer een proces en exporteer alle content:

```bash
python run_import_and_export.py \
  --input examples/process_onboard_account.json \
  --schema examples/process_schema.json
```

Output: `export/export_with_content.json`

### 2. Alleen Importeren

```bash
python main.py \
  --input examples/process_onboard_account.json \
  --schema examples/process_schema.json
```

### 3. Alleen Exporteren

```bash
python exporter.py --output export_latest.json
```

## Projectstructuur

```
digitalecoach_client/
├── main.py                      # Importer CLI
├── exporter.py                  # Exporter CLI
├── run_import_and_export.py     # Combined workflow
├── askdelphi/
│   ├── session.py              # AskDelphi API client
│   └── exceptions.py           # Custom exceptions
├── importer/
│   ├── mapper.py               # JSON → Topic tree mapper
│   ├── importer.py             # Topic importer
│   └── validator.py            # JSON schema validator
├── config/
│   └── env.py                  # Environment configuration
├── examples/
│   ├── process_onboard_account.json
│   └── process_schema.json
└── export/                     # Export output folder
```

## Workflow Details

### Import + Export (`run_import_and_export.py`)

1. **Reset mockserver** - Clears previous data
2. **Load & validate** - Loads process JSON and validates against schema
3. **Map to topics** - Converts process JSON to topic tree
4. **Import** - Creates topics in AskDelphi
5. **Export** - Exports all content as JSON

### Importer (`main.py`)

Imports a process JSON file into AskDelphi:
- Validates against JSON schema
- Maps to internal topic tree structure
- Creates topics with proper hierarchy
- Handles topic types and metadata

### Exporter (`exporter.py`)

Exports all content from AskDelphi as JSON:
- Fetches all topics
- Includes topic types
- Includes parts and relations
- Conforms to AskDelphi export format

## Topic Hierarchy

```
Process (Digitale Coach Homepagina)
├── Task (Digitale Coach Procespagina)
│   ├── Step (Digitale Coach Stap)
│   │   └── Instruction (Digitale Coach Instructie)
```

## Testing

Run tests:

```bash
pytest
```

Tests validate:
- Authentication and connection
- Content export
- Complete import workflow

## Environment Variables

- `ASKDELPHI_BASE_URL` - AskDelphi API base URL (default: http://localhost:8000)
- `ASKDELPHI_API_KEY` - API key for authentication
- `ASKDELPHI_TENANT` - Tenant ID
- `ASKDELPHI_NT_ACCOUNT` - NT account name
- `ASKDELPHI_ACL` - ACL entry (comma-separated)
- `ASKDELPHI_PROJECT_ID` - Project ID
- `DEBUG` - Enable debug logging (default: false)
>>>>>>> 6c2c8d8 (Initial commit: AskDelphi client with import/export)
