#!/usr/bin/env python3
"""Add topic_type_id and topic_type_title fields to all topics in process JSON.

This script enriches the process JSON with explicit topic type information,
ensuring all topics have both the UUID ID and human-readable title for the topic type.

Usage:
    python add_topic_type_fields.py input.json output.json
    
Example:
    python add_topic_type_fields.py procesbeschrijving/process_sanering_uuid.json procesbeschrijving/process_sanering_enriched.json
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, Any, List

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Topic type mappings: name -> (id, title)
TOPIC_TYPE_MAPPING = {
    "Digitale Coach Homepagina": ("a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6", "Digitale Coach Homepagina"),
    "Digitale Coach Procespagina": ("b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7", "Digitale Coach Procespagina"),
    "Digitale Coach Stap": ("c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8", "Digitale Coach Stap"),
    "Digitale Coach Instructie": ("d4e5f6a7-b8c9-4adb-e2f3-a4b5c6d7e8f9", "Digitale Coach Instructie"),
    "Task": ("c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8", "Digitale Coach Stap"),
    "Action": ("c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8", "Digitale Coach Stap"),
    "Simple topic": ("d4e5f6a7-b8c9-4adb-e2f3-a4b5c6d7e8f9", "Digitale Coach Instructie"),
}


def get_topic_type_info(topic_type_name: str) -> tuple:
    """Get topic type ID and title for a given type name."""
    if topic_type_name in TOPIC_TYPE_MAPPING:
        return TOPIC_TYPE_MAPPING[topic_type_name]
    
    # Default to Digitale Coach Stap if not found
    print(f"Warning: Unknown topic type '{topic_type_name}', using default 'Digitale Coach Stap'")
    return TOPIC_TYPE_MAPPING["Digitale Coach Stap"]


def enrich_topic(topic: Dict[str, Any], parent_type: str = "Digitale Coach Homepagina") -> None:
    """Add topic_type_id and topic_type_title to a topic."""
    
    # Determine the topic type
    if "topic_type_id" not in topic and "topic_type_title" not in topic:
        topic_type_name = topic.get("topicType", parent_type)
        topic_type_id, topic_type_title = get_topic_type_info(topic_type_name)
        
        topic["topic_type_id"] = topic_type_id
        topic["topic_type_title"] = topic_type_title
        
        print(f"  ✓ Added type fields to '{topic.get('title', 'Unknown')}': {topic_type_title}")


def enrich_process(process_data: Dict[str, Any]) -> None:
    """Recursively add topic type fields to all topics in the process."""
    
    process = process_data.get("process", {})
    
    # Enrich root process
    enrich_topic(process, "Digitale Coach Homepagina")
    root_type = process.get("topic_type_title", "Digitale Coach Homepagina")
    
    # Enrich tasks
    for task in process.get("tasks", []):
        enrich_topic(task, "Digitale Coach Stap")
        task_type = task.get("topic_type_title", "Digitale Coach Stap")
        
        # Enrich steps within task
        for step in task.get("steps", []):
            enrich_topic(step, "Digitale Coach Stap")
            step_type = step.get("topic_type_title", "Digitale Coach Stap")
            
            # Enrich instructions within step
            for instruction in step.get("instructions", []):
                enrich_topic(instruction, "Digitale Coach Instructie")
    
    # Enrich steps at root level
    for step in process.get("steps", []):
        enrich_topic(step, "Digitale Coach Stap")
        step_type = step.get("topic_type_title", "Digitale Coach Stap")
        
        # Enrich instructions within step
        for instruction in step.get("instructions", []):
            enrich_topic(instruction, "Digitale Coach Instructie")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Error: Input file required")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"Loading process file: {input_file}")
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        process_data = json.load(f)
    
    print("Enriching process with topic type fields...")
    enrich_process(process_data)
    
    print(f"\nSaving enriched process to: {output_file}")
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(process_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Done! All topics now have topic_type_id and topic_type_title fields.")


if __name__ == "__main__":
    main()
