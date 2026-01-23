#!/usr/bin/env python3
"""Debug script for ERR20001 validation errors during topic creation.

This script helps diagnose why topic creation fails with validation errors
by testing different payload combinations and logging detailed information.

Usage:
    python debug_validation_error.py [input_file]
    
Example:
    python debug_validation_error.py procesbeschrijving/process_sanering_uuid.json
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api_client.session import AskDelphiSession
from src.config.env import ASKDELPHI_BASE_URL, ASKDELPHI_API_KEY, ASKDELPHI_TENANT
from src.importer.mapper import DigitalCoachMapper, TopicNode


def test_payload_variations(session: AskDelphiSession, topic: TopicNode) -> None:
    """Test different payload variations to identify validation requirements."""
    
    print("\n" + "="*80)
    print(f"Testing topic: {topic.title} (ID: {topic.id})")
    print(f"Type: {topic.topic_type.get('title')} (Key: {topic.topic_type.get('key')})")
    print(f"Parent: {topic.parent_id}")
    print("="*80 + "\n")
    
    # Base payload
    base_payload = {
        "topicId": topic.id,
        "topicTitle": topic.title,
        "topicTypeId": str(topic.topic_type["key"]),
        "copyParentTags": False,
    }
    
    # Variations to test
    variations = [
        {
            "name": "Minimal (base only)",
            "payload": base_payload.copy()
        },
        {
            "name": "With language",
            "payload": {**base_payload, "language": "nl-NL"}
        },
        {
            "name": "With parentTopicId",
            "payload": {
                **base_payload,
                "language": "nl-NL",
                "parentTopicId": topic.parent_id
            } if topic.parent_id else base_payload.copy()
        },
        {
            "name": "With status",
            "payload": {
                **base_payload,
                "language": "nl-NL",
                "status": "Published"
            }
        },
        {
            "name": "Full with all fields",
            "payload": {
                **base_payload,
                "language": "nl-NL",
                "parentTopicId": topic.parent_id,
                "status": "Published",
                "contentType": "RichText"
            } if topic.parent_id else {
                **base_payload,
                "language": "nl-NL",
                "status": "Published",
                "contentType": "RichText"
            }
        }
    ]
    
    for variation in variations:
        print(f"\n[TEST] {variation['name']}")
        print(f"Payload: {json.dumps(variation['payload'], indent=2)}")
        
        try:
            result = session.post(
                f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
                json=variation['payload']
            )
            print(f"✓ SUCCESS")
            print(f"Response: {json.dumps(result, indent=2)}")
            return  # Stop on first success
        except Exception as e:
            error_msg = str(e)
            print(f"✗ FAILED: {error_msg}")
            
            # Try to extract error details
            if "ERR20001" in error_msg:
                print("  → Validation error (ERR20001)")
            elif "400" in error_msg:
                print("  → Bad request (400)")
            elif "401" in error_msg or "auth" in error_msg.lower():
                print("  → Authentication error")
            else:
                print(f"  → Other error: {type(e).__name__}")


def analyze_process_file(input_file: str) -> None:
    """Analyze a process JSON file and test topic creation."""
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"Loading process file: {input_file}")
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        process_data = json.load(f)
    
    # Map process to topics
    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(process_data)
    
    print(f"\nFound {len(root_topics)} root topic(s)")
    
    # Initialize session
    print(f"\nInitializing AskDelphi session...")
    print(f"  Base URL: {ASKDELPHI_BASE_URL}")
    print(f"  Tenant: {ASKDELPHI_TENANT}")
    
    try:
        session = AskDelphiSession(
            base_url=ASKDELPHI_BASE_URL,
            api_key=ASKDELPHI_API_KEY,
            tenant=ASKDELPHI_TENANT
        )
        print("✓ Session initialized")
    except Exception as e:
        print(f"✗ Failed to initialize session: {e}")
        sys.exit(1)
    
    # Test first root topic
    if root_topics:
        root_topic = root_topics[0]
        test_payload_variations(session, root_topic)
        
        # Test first child if available
        if root_topic.children:
            print("\n" + "-"*80)
            child_topic = root_topic.children[0]
            test_payload_variations(session, child_topic)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Error: Input file required")
        sys.exit(1)
    
    input_file = sys.argv[1]
    analyze_process_file(input_file)


if __name__ == "__main__":
    main()
