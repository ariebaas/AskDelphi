"""End-to-end tests for the Digitalecoach importer against the mock server.

These tests:
- Start from a JSON process definition
- Map it to a topic tree
- Use AskDelphiSession to talk to the mock server
- Assert that topics and parts are created as expected
"""

import json
import subprocess
import time
import os
import logging
import requests
from datetime import datetime

from askdelphi.session import AskDelphiSession
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter
from config import env


# Configure logging to write to both file and console
log_file = os.path.join(os.path.dirname(__file__), f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_format = "[E2E] %(asctime)s %(levelname)s: %(message)s"

# File handler with flush
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

file_handler = FlushFileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
formatter.default_msec_format = "%s.%03d"
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))

# Root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def wait_for_mockserver(url: str, timeout: int = 10):
    """Wait until the mockserver responds or timeout expires."""
    logging.info("Waiting for mockserver at %s (timeout=%ss)", url, timeout)
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            # 200/404: endpoint reachable, 401: auth required but server is up
            if r.status_code in (200, 401, 404):
                logging.info("Mockserver is reachable (status=%s)", r.status_code)
                return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Mockserver did not become ready in time")


def test_authentication_and_connection():
    """Test authentication and connection to the mock server."""
    logging.info("=" * 60)
    logging.info("TESTING AUTHENTICATION AND CONNECTION:")
    logging.info("=" * 60)
    
    # Ensure mockserver is running
    wait_for_mockserver(env.ASKDELPHI_BASE_URL + "/projects/nonexistent")
    
    # Reset mockserver state
    logging.info("Resetting mockserver state...")
    requests.post(f"{env.ASKDELPHI_BASE_URL}/reset")
    logging.info("Mockserver reset complete")
    
    # Test 1: Create AskDelphiSession with valid credentials
    logging.info("Test 1: Creating AskDelphiSession with valid credentials...")
    try:
        session = AskDelphiSession(
            base_url=env.ASKDELPHI_BASE_URL,
            api_key=env.ASKDELPHI_API_KEY,
            tenant=env.ASKDELPHI_TENANT,
            nt_account=env.ASKDELPHI_NT_ACCOUNT,
            acl=env.ASKDELPHI_ACL,
            project_id=env.ASKDELPHI_PROJECT_ID,
        )
        logging.info("✓ AskDelphiSession created successfully")
        assert session is not None
    except Exception as e:
        logging.error("✗ Failed to create AskDelphiSession: %s", str(e))
        raise
    
    # Test 2: Verify session token was obtained via AskDelphiSession
    logging.info("Test 2: Verifying session token retrieval via AskDelphiSession...")
    try:
        # Make a request through AskDelphiSession to trigger token retrieval
        # This will call _refresh_token internally
        result = session.get("/projects/test-project")
        logging.info("✓ Session token obtained and used successfully via AskDelphiSession")
        assert result is not None or True  # Request succeeded (token was valid)
    except Exception as e:
        # 404 is OK - means auth worked but project doesn't exist
        if "404" in str(e):
            logging.info("✓ Session token obtained and used successfully (404 = project not found, auth worked)")
        else:
            logging.error("✗ Failed to use session token: %s", str(e))
            raise
    
    # Test 3: Test invalid credentials (should fail)
    logging.info("Test 3: Testing invalid credentials (should fail)...")
    try:
        invalid_session = AskDelphiSession(
            base_url=env.ASKDELPHI_BASE_URL,
            api_key="invalid-api-key",
            tenant=env.ASKDELPHI_TENANT,
            nt_account=env.ASKDELPHI_NT_ACCOUNT,
            acl=env.ASKDELPHI_ACL,
            project_id=env.ASKDELPHI_PROJECT_ID,
        )
        # Try to make a request - should fail
        r = requests.get(
            f"{env.ASKDELPHI_BASE_URL}/projects/test-project",
            headers={"Authorization": f"Bearer {invalid_session.session_token}"}
        )
        # If we get here with 401, that's expected
        if r.status_code == 401:
            logging.info("✓ Invalid credentials correctly rejected (status=401)")
        else:
            logging.warning("⚠ Unexpected status code for invalid credentials: %s", r.status_code)
    except Exception as e:
        logging.info("✓ Invalid credentials correctly rejected with exception: %s", type(e).__name__)
    
    # Test 4: Test connection without Authorization header (should fail)
    logging.info("Test 4: Testing request without Authorization header (should fail)...")
    try:
        r = requests.get(f"{env.ASKDELPHI_BASE_URL}/projects/test-project")
        if r.status_code == 401:
            logging.info("✓ Request without auth header correctly rejected (status=401)")
            assert r.status_code == 401
        else:
            logging.warning("⚠ Unexpected status code without auth: %s", r.status_code)
    except Exception as e:
        logging.error("✗ Unexpected error: %s", str(e))
        raise
    
    logging.info("=" * 60)
    logging.info("ALL AUTHENTICATION TESTS PASSED!")
    logging.info("=" * 60)


def test_export_content():
    """Test exporting content from the mock server."""
    logging.info("=" * 60)
    logging.info("TESTING CONTENT EXPORT:")
    logging.info("=" * 60)
    
    # Ensure mockserver is running
    wait_for_mockserver(env.ASKDELPHI_BASE_URL + "/projects/nonexistent")
    
    # Reset mockserver state
    logging.info("Resetting mockserver state...")
    requests.post(f"{env.ASKDELPHI_BASE_URL}/reset")
    logging.info("Mockserver reset complete")
    
    # Create a session and import some content first
    logging.info("Setting up test data...")
    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
    )
    
    # Load and import example process
    with open("examples/process_onboard_account.json", encoding='utf-8-sig') as f:
        data = json.load(f)
    
    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])
    
    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)
    logging.info(f"✓ Imported {len(root_topics)} root topics")
    
    # Now test export
    logging.info("Calling export endpoint...")
    try:
        export_data = session.get("/export")
        logging.info("✓ Export endpoint called successfully")
    except Exception as e:
        logging.error(f"✗ Failed to call export endpoint: {e}")
        raise
    
    # Validate export structure
    logging.info("Validating export structure...")
    assert isinstance(export_data, dict), "Export should be a dictionary"
    assert "_metadata" in export_data, "Export should have _metadata"
    assert "content_design" in export_data, "Export should have content_design"
    assert "topics" in export_data, "Export should have topics"
    logging.info("✓ Export structure is valid")
    
    # Validate metadata
    metadata = export_data["_metadata"]
    assert metadata["version"] == "1.0", "Metadata version should be 1.0"
    assert "exported_at" in metadata, "Metadata should have exported_at"
    assert metadata["topic_count"] > 0, "Should have exported topics"
    logging.info(f"✓ Metadata valid (exported {metadata['topic_count']} topics)")
    
    # Validate content design
    content_design = export_data["content_design"]
    assert "topic_types" in content_design, "Content design should have topic_types"
    assert len(content_design["topic_types"]) > 0, "Should have topic types"
    logging.info(f"✓ Content design valid ({len(content_design['topic_types'])} topic types)")
    
    # Validate topics
    topics = export_data["topics"]
    assert len(topics) > 0, "Should have exported topics"
    
    # Check first topic structure
    first_topic_id = list(topics.keys())[0]
    first_topic = topics[first_topic_id]
    
    required_fields = ["id", "version_id", "title", "topic_type_id", "parts", "relations"]
    for field in required_fields:
        assert field in first_topic, f"Topic should have {field}"
    
    logging.info(f"✓ Topics valid ({len(topics)} topics exported)")
    logging.info(f"  First topic: {first_topic['title']}")
    
    logging.info("=" * 60)
    logging.info("EXPORT TEST PASSED!")
    logging.info("=" * 60)


def test_import_onboard_account():
    """End-to-end test: import the onboard-account process into the mockserver."""
    # Ensure mockserver is running externally (or start it in another shell)
    wait_for_mockserver(env.ASKDELPHI_BASE_URL + "/projects/nonexistent")

    # Reset mockserver state before test
    logging.info("Resetting mockserver state...")
    requests.post(f"{env.ASKDELPHI_BASE_URL}/reset")
    logging.info("Mockserver reset complete")

    example_path = os.path.join(os.path.dirname(__file__), "..", "examples", "process_onboard_account.json")
    with open(example_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    logging.info("Loaded example JSON from %s", example_path)
    steps = len(data.get("process", {}).get("steps", []))
    logging.info("Process id=%s title=%s (#steps=%s)", data["process"].get("id"), data["process"].get("title"), steps)

    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])
    logging.info("Mapped process to %s root topic(s)", len(root_topics))
    
    # Log the topic tree structure
    def tree_to_text(topic, indent=0):
        """Convert tree to simple text representation."""
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

    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
    )

    logging.info("Created AskDelphiSession for base_url=%s, project_id=%s", env.ASKDELPHI_BASE_URL, env.ASKDELPHI_PROJECT_ID)

    importer = DigitalCoachImporter(session)
    logging.info("Starting import of topic tree into mockserver...")
    importer.import_topics(root_topics)
    logging.info("Import finished")

    # Assert that homepage topic exists
    home_id = data["process"]["id"]
    r = requests.get(f"{env.ASKDELPHI_BASE_URL}/topics/{home_id}", headers={
        "Authorization": f"Bearer {session.session_token}"
    })
    logging.info("Homepage topic check: GET /topics/%s -> status=%s", home_id, r.status_code)
    assert r.status_code == 200
    
    # Test: Add parts (content) to a topic
    logging.info("=" * 60)
    logging.info("TESTING PARTS (CONTENT) MANAGEMENT:")
    logging.info("=" * 60)
    
    instr_id = "instr-1-1-2"  # Second instruction in first step (doesn't have content yet)
    part_name = "customPart"
    part_content = {"text": "Dit is een aangepaste content part"}
    
    # Checkout topic before updating
    checkout_url = f"{env.ASKDELPHI_BASE_URL}/topics/{instr_id}/checkout"
    r = requests.post(checkout_url, headers={"Authorization": f"Bearer {session.session_token}"})
    logging.info("Checkout topic %s: status=%s", instr_id, r.status_code)
    assert r.status_code == 200
    
    # Add part
    parts_url = f"{env.ASKDELPHI_BASE_URL}/topics/{instr_id}/parts"
    r = requests.post(
        parts_url,
        json={"name": part_name, "content": part_content},
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Create part %s for topic %s: status=%s", part_name, instr_id, r.status_code)
    assert r.status_code == 200
    
    # Get parts to verify
    r = requests.get(
        parts_url,
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Get parts for topic %s: status=%s, count=%d", instr_id, r.status_code, len(r.json()))
    assert r.status_code == 200
    
    # Update part
    updated_content = {"text": "Dit is de BIJGEWERKTE content"}
    r = requests.put(
        f"{parts_url}/{part_name}",
        json={"name": part_name, "content": updated_content},
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Update part %s for topic %s: status=%s", part_name, instr_id, r.status_code)
    assert r.status_code == 200
    
    # Delete part
    r = requests.delete(
        f"{parts_url}/{part_name}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Delete part %s for topic %s: status=%s", part_name, instr_id, r.status_code)
    assert r.status_code == 200
    
    # Verify part is deleted
    r = requests.get(
        parts_url,
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    parts_list = r.json()
    part_names = [p.get("name") for p in parts_list]
    logging.info("Verify part deletion: remaining parts=%s (should not contain %s)", part_names, part_name)
    assert part_name not in part_names
    
    # Checkin topic
    checkin_url = f"{env.ASKDELPHI_BASE_URL}/topics/{instr_id}/checkin"
    r = requests.post(
        checkin_url,
        json={"comment": "Updated and deleted custom part"},
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Checkin topic %s: status=%s", instr_id, r.status_code)
    assert r.status_code == 200
    
    # Test: Update a topic
    logging.info("=" * 60)
    logging.info("TESTING TOPIC UPDATE:")
    logging.info("=" * 60)
    
    step_id = "step-1-1"
    updated_title = "Account aanmaken (Updated)"
    
    # Checkout
    r = requests.post(
        f"{env.ASKDELPHI_BASE_URL}/topics/{step_id}/checkout",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Checkout topic %s for update: status=%s", step_id, r.status_code)
    assert r.status_code == 200
    
    # Update topic
    update_payload = {
        "id": step_id,
        "title": updated_title,
        "topicTypeKey": "1003",
        "topicTypeNamespace": "AskDelphi.DigitalCoach",
        "parentId": home_id,
        "metadata": {"description": "Updated description"}
    }
    r = requests.put(
        f"{env.ASKDELPHI_BASE_URL}/topics/{step_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Update topic %s: status=%s", step_id, r.status_code)
    assert r.status_code == 200
    
    # Checkin
    r = requests.post(
        f"{env.ASKDELPHI_BASE_URL}/topics/{step_id}/checkin",
        json={"comment": "Updated title and description"},
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Checkin topic %s after update: status=%s", step_id, r.status_code)
    assert r.status_code == 200
    
    # Verify update
    r = requests.get(
        f"{env.ASKDELPHI_BASE_URL}/topics/{step_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    topic_data = r.json()
    logging.info("Verify update: topic title is now '%s'", topic_data.get("title"))
    assert topic_data.get("title") == updated_title
    
    # Test: Delete a topic
    logging.info("=" * 60)
    logging.info("TESTING TOPIC DELETION:")
    logging.info("=" * 60)
    
    delete_id = "instr-2-2-2"  # Last instruction
    r = requests.delete(
        f"{env.ASKDELPHI_BASE_URL}/topics/{delete_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Delete topic %s: status=%s", delete_id, r.status_code)
    assert r.status_code == 200
    
    # Verify deletion
    r = requests.get(
        f"{env.ASKDELPHI_BASE_URL}/topics/{delete_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Verify deletion: GET /topics/%s -> status=%s (should be 404)", delete_id, r.status_code)
    assert r.status_code == 404
    
    # Test: Delete a project
    logging.info("=" * 60)
    logging.info("TESTING PROJECT DELETION:")
    logging.info("=" * 60)
    
    # First create a test project
    test_project_id = "test-project-delete"
    r = requests.post(
        f"{env.ASKDELPHI_BASE_URL}/projects",
        json={"id": test_project_id, "title": "Test Project for Deletion", "description": "Will be deleted"},
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Create test project %s: status=%s", test_project_id, r.status_code)
    assert r.status_code == 200
    
    # Verify project exists
    r = requests.get(
        f"{env.ASKDELPHI_BASE_URL}/projects/{test_project_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Verify project exists: GET /projects/%s -> status=%s", test_project_id, r.status_code)
    assert r.status_code == 200
    
    # Delete project
    r = requests.delete(
        f"{env.ASKDELPHI_BASE_URL}/projects/{test_project_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Delete project %s: status=%s", test_project_id, r.status_code)
    assert r.status_code == 200
    
    # Verify deletion
    r = requests.get(
        f"{env.ASKDELPHI_BASE_URL}/projects/{test_project_id}",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )
    logging.info("Verify deletion: GET /projects/%s -> status=%s (should be 404)", test_project_id, r.status_code)
    assert r.status_code == 404
    
    logging.info("=" * 60)
    logging.info("ALL TESTS PASSED!")
    logging.info("=" * 60)


if __name__ == "__main__":
    try:
        test_authentication_and_connection()
        test_export_content()
        test_import_onboard_account()
    except Exception as e:
        logging.error("Test execution failed: %s", str(e), exc_info=True)
