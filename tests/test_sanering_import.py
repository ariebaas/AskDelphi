#!/usr/bin/env python3
"""Test script om process_sanering.json te importeren, testen en exporteren met relations support."""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()

os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from askdelphi.session import AskDelphiSession
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter
import config.env as env_config
import requests

project_root = os.path.dirname(os.path.dirname(__file__))
log_dir = os.path.join(project_root, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"sanering_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_format = "[SANERING] %(asctime)s %(levelname)s: %(message)s"


class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


file_handler = FlushFileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG if env_config.DEBUG else logging.INFO)
formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
formatter.default_msec_format = "%s.%03d"
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if env_config.DEBUG else logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if env_config.DEBUG else logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

if env_config.DEBUG:
    logging.info("DEBUG MODE ENABLED - Verbose logging active")


def wait_for_mockserver(url, timeout=10):
    """Wait for mockserver to be ready."""
    import time
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url, timeout=1)
            return
        except:
            time.sleep(0.5)
    raise RuntimeError("Mockserver did not become ready in time")


def test_sanering_import():
    """Import process_sanering.json and test relations."""
    logging.info("=" * 60)
    logging.info("IMPORTING PROCESS_SANERING.JSON WITH RELATIONS SUPPORT")
    logging.info("=" * 60)
    
    # Wait for mockserver
    wait_for_mockserver(env_config.ASKDELPHI_BASE_URL + "/projects/nonexistent")
    
    # Reset mockserver
    logging.info("Resetting mockserver state...")
    requests.post(f"{env_config.ASKDELPHI_BASE_URL}/reset")
    logging.info("✓ Mockserver reset complete")
    
    # Load process_sanering.json
    example_path = os.path.join(os.path.dirname(__file__), "..", "procesbeschrijving", "process_sanering.json")
    with open(example_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    logging.info("Loaded process_sanering.json from %s", example_path)
    process = data["process"]
    logging.info("Process: id=%s, title=%s, tasks=%d", process.get("id"), process.get("title"), len(process.get("tasks", [])))
    
    # Map process to topics
    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(process)
    logging.info("✓ Mapped process to %d root topic(s)", len(root_topics))
    
    # Log topic tree
    def tree_to_text(topic, indent=0):
        lines = []
        prefix = "  " * indent
        if indent > 0:
            prefix += "├─ "
        lines.append(f"{prefix}[{topic.id}] {topic.title} ({topic.topic_type.get('title', 'unknown')})")
        for child in topic.children:
            lines.extend(tree_to_text(child, indent + 1))
        return lines
    
    for root_topic in root_topics:
        tree_lines = tree_to_text(root_topic)
        tree_str = "\n".join(tree_lines)
        logging.info("TOPIC TREE STRUCTURE:\n%s", tree_str)
    
    # Create session and import
    session = AskDelphiSession(
        base_url=env_config.ASKDELPHI_BASE_URL,
        api_key=env_config.ASKDELPHI_API_KEY,
        tenant=env_config.ASKDELPHI_TENANT,
        nt_account=env_config.ASKDELPHI_NT_ACCOUNT,
        acl=env_config.ASKDELPHI_ACL,
        project_id=env_config.ASKDELPHI_PROJECT_ID,
        use_auth_cache=env_config.USE_AUTH_CACHE,
    )
    
    logging.info("Created AskDelphiSession for base_url=%s", env_config.ASKDELPHI_BASE_URL)
    
    importer = DigitalCoachImporter(session)
    logging.info("Starting import of topic tree...")
    importer.import_topics(root_topics)
    logging.info("✓ Import finished")
    
    # Verify import
    logging.info("=" * 60)
    logging.info("VERIFYING IMPORT AND RELATIONS")
    logging.info("=" * 60)
    
    root_id = process["id"]
    root_topic = session.get(f"/topics/{root_id}")
    
    logging.info("✓ Root topic retrieved: %s", root_topic.get("title"))
    logging.info("  Relations: parent=%s, children=%d", 
                 root_topic.get("relations", {}).get("parent"),
                 len(root_topic.get("relations", {}).get("children", [])))
    
    # Test export
    logging.info("=" * 60)
    logging.info("EXPORTING CONTENT")
    logging.info("=" * 60)
    
    export_data = session.get("/export")
    
    logging.info("✓ Export retrieved")
    logging.info("  Topics exported: %d", export_data["_metadata"]["topic_count"])
    logging.info("  Exported at: %s", export_data["_metadata"]["exported_at"])
    
    # Validate relations in export
    logging.info("=" * 60)
    logging.info("VALIDATING RELATIONS IN EXPORT")
    logging.info("=" * 60)
    
    topics = export_data["topics"]
    relations_count = 0
    children_count = 0
    
    for topic_id, topic in topics.items():
        relations = topic.get("relations", {})
        if relations.get("children"):
            relations_count += 1
            children_count += len(relations["children"])
            logging.info("  Topic %s: %d children", topic.get("title"), len(relations["children"]))
    
    logging.info("✓ Relations validation complete")
    logging.info("  Topics with children: %d", relations_count)
    logging.info("  Total child relations: %d", children_count)
    
    # Save export to file
    export_file = os.path.join(log_dir, f"export_sanering_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    logging.info("✓ Export saved to %s", export_file)
    
    logging.info("=" * 60)
    logging.info("ALL TESTS PASSED!")
    logging.info("=" * 60)


if __name__ == "__main__":
    try:
        test_sanering_import()
    except Exception as e:
        logging.error("Test execution failed: %s", str(e), exc_info=True)
        sys.exit(1)
