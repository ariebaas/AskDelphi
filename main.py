"""Ingangspunt voor de Digitalecoach referentie importer.

Dit script:
- Laadt configuratie uit .env
- Valideert de input JSON tegen een schema
- Mapt het proces naar een topic tree
- Verwijdert bestaand proces indien aanwezig
- Importeert alles in AskDelphi via AskDelphiSession
"""

import json
import argparse
import logging

from api_client.session import AskDelphiSession
from api_client.exceptions import AskDelphiNotFoundError
from config import env
from importer.validator import ProcessValidator
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter

logger = logging.getLogger(__name__)


def delete_process_if_exists(session: AskDelphiSession, process_id: str) -> None:
    """Verwijder bestaand proces en alle bijbehorende topics recursief.
    
    Args:
        session: AskDelphiSession voor API communicatie
        process_id: Proces ID om te verwijderen
    """
    try:
        logger.info(f"Controleren of proces '{process_id}' al bestaat...")
        topic = session.get(f"/topics/{process_id}")
        logger.info(f"Proces '{process_id}' gevonden. Verwijderen inclusief alle child topics...")
        
        _delete_topic_recursive(session, process_id)
        logger.info(f"✓ Proces '{process_id}' en alle child topics succesvol verwijderd")
    except AskDelphiNotFoundError:
        logger.info(f"Proces '{process_id}' bestaat niet, geen verwijdering nodig")
    except Exception as e:
        logger.warning(f"Kon proces niet verwijderen: {e}")


def _delete_topic_recursive(session: AskDelphiSession, topic_id: str) -> None:
    """Verwijder een topic en alle bijbehorende child topics recursief.
    
    Args:
        session: AskDelphiSession voor API communicatie
        topic_id: Topic ID om te verwijderen
    """
    try:
        topic = session.get(f"/topics/{topic_id}")
        
        relations = topic.get("relations", {})
        children = relations.get("children", [])
        
        for child_id in children:
            _delete_topic_recursive(session, child_id)
        
        session.delete(f"/topics/{topic_id}")
        logger.debug(f"  Verwijderd topic: {topic_id}")
    except Exception as e:
        logger.debug(f"  Kon topic {topic_id} niet verwijderen: {e}")


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
        use_auth_cache=False,
    )

    process_id = data["process"].get("id")
    delete_process_if_exists(session, process_id)

    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digitalecoach referentie importer")
    parser.add_argument("--input", required=True, help="Pad naar proces JSON bestand")
    parser.add_argument("--schema", required=True, help="Pad naar JSON schema bestand")
    args = parser.parse_args()

    run(args.input, args.schema)
