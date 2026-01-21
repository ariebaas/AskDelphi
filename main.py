"""Ingangspunt voor de Digitalecoach referentie importer.

Dit script:
- Laadt configuratie uit .env
- Valideert de input JSON tegen een schema
- Mapt het proces naar een topic tree
- Importeert alles in AskDelphi via AskDelphiSession
"""

import json
import argparse

from api_client.session import AskDelphiSession
from config import env
from importer.validator import ProcessValidator
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter


def run(input_file: str, schema_file: str) -> None:
    """Voer de volledige import pipeline uit voor een gegeven proces JSON bestand."""
    with open(input_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    validator = ProcessValidator(schema_file)
    validator.validate(data)

    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])

    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
    )

    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digitalecoach referentie importer")
    parser.add_argument("--input", required=True, help="Pad naar proces JSON bestand")
    parser.add_argument("--schema", required=True, help="Pad naar JSON schema bestand")
    args = parser.parse_args()

    run(args.input, args.schema)
