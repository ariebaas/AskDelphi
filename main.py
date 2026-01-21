"""Ingangspunt voor de Digitalecoach referentie importer.

Dit script:
- Laadt configuratie uit .env
- Valideert de input JSON tegen een schema
- Mapt het proces naar een topic tree
- Verwijdert bestaand proces indien aanwezig
- Importeert alles in AskDelphi via AskDelphiSession
- Genereert log file en export JSON
"""

import json
import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

from api_client.session import AskDelphiSession
from api_client.exceptions import AskDelphiNotFoundError
from config import env
from importer.validator import ProcessValidator
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter

log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'import_{timestamp}.log')

class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

file_handler = FlushFileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

main_logger = logging.getLogger(__name__)


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
    main_logger.info("=" * 70)
    main_logger.info("IMPORT WORKFLOW GESTART")
    main_logger.info("=" * 70)
    
    with open(input_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    main_logger.info(f"✓ Proces geladen: {input_file}")

    validator = ProcessValidator(schema_file)
    validator.validate(data)
    main_logger.info(f"✓ Schema gevalideerd: {schema_file}")

    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])

    use_auth_cache = env.USE_AUTH_CACHE if hasattr(env, 'USE_AUTH_CACHE') else False
    
    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
        use_auth_cache=use_auth_cache,
    )

    process_id = data["process"].get("id")
    delete_process_if_exists(session, process_id)

    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)
    
    # Export data after import
    main_logger.info("\nExport van alle content...")
    try:
        export_data = session.get("/export")
        
        # Save export to JSON file
        export_file = os.path.join(log_dir, f'export_{timestamp}.json')
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        main_logger.info(f"✓ Export opgeslagen: {export_file}")
        
        # Print summary
        if isinstance(export_data, dict):
            metadata = export_data.get("_metadata", {})
            topic_count = metadata.get("topic_count", 0)
            main_logger.info("\n" + "=" * 70)
            main_logger.info("IMPORT SUCCESVOL VOLTOOID!")
            main_logger.info("=" * 70)
            main_logger.info(f"Log file: {log_file}")
            main_logger.info(f"Export file: {export_file}")
            main_logger.info(f"Topics geïmporteerd: {topic_count}")
            main_logger.info("=" * 70)
    except Exception as e:
        main_logger.error(f"✗ Export mislukt: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digitalecoach referentie importer")
    parser.add_argument("--input", required=True, help="Pad naar proces JSON bestand")
    parser.add_argument("--schema", required=True, help="Pad naar JSON schema bestand")
    args = parser.parse_args()

    run(args.input, args.schema)
