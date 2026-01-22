"""Test script voor alle CRUD operaties conform AskDelphi API.

Dit script test alle 10 CRUD operaties:
- CREATE (v4)
- READ (v1)
- READ Parts (v3)
- UPDATE Part (v2)
- UPDATE Metadata (v2)
- DELETE (v3)
- CHECKOUT (v3)
- CHECKIN (v4)
- ADD Relation (v2)
- ADD Tag (v2)
"""

import pytest
import uuid
import logging
import os
import requests
import time
from pathlib import Path

from src.api_client.session import AskDelphiSession
from src.api_client.topic import TopicService
from src.api_client.parts import PartService
from src.api_client.checkout import CheckoutService
from src.api_client.relations import RelationService
from src.config import env

logger = logging.getLogger(__name__)

# Zet auth mode op traditional (niet cache)
os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

# Verwijder cache file
cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()


def wait_for_mockserver(url: str, timeout: int = 5):
    """Wacht totdat de mockserver reageert."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code in (200, 401, 404):
                return True
        except Exception:
            time.sleep(0.2)
    return False


@pytest.fixture(scope="session", autouse=True)
def setup_mockserver():
    """Setup mockserver voor alle tests."""
    logger.info("Checking mockserver...")
    if not wait_for_mockserver(env.ASKDELPHI_BASE_URL + "/projects/test"):
        logger.warning("Mockserver niet bereikbaar - tests kunnen falen")
    
    # Reset mockserver
    try:
        requests.post(f"{env.ASKDELPHI_BASE_URL}/reset")
        logger.info("Mockserver reset")
    except Exception as e:
        logger.warning(f"Kon mockserver niet resetten: {e}")


@pytest.fixture
def session():
    """Maak AskDelphiSession voor tests."""
    return AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
        use_auth_cache=False,
    )


@pytest.fixture
def services(session):
    """Maak alle services voor tests."""
    return {
        'topic': TopicService(session),
        'parts': PartService(session),
        'checkout': CheckoutService(session),
        'relations': RelationService(session),
    }


class TestCRUDOperations:
    """Test alle CRUD operaties."""

    def test_01_create_topic(self, session):
        """Test CREATE operatie (v4)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        assert result is not None
        assert "topicId" in result or "id" in result
        logger.info(f"✅ CREATE: Topic aangemaakt: {topic_id}")

    def test_02_read_topic(self, services, session):
        """Test READ operatie (v1)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak eerst topic aan
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        # Lees topic
        result = services['topic'].get_topic(topic_id)
        assert result is not None
        logger.info(f"✅ READ: Topic gelezen: {topic_id}")

    def test_03_checkout_topic(self, services, session):
        """Test CHECKOUT operatie (v3)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak eerst topic aan
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        # Checkout topic
        result = services['checkout'].checkout(topic_id)
        assert result is not None
        logger.info(f"✅ CHECKOUT: Topic uitgecheckt: {topic_id}")
        
        return topic_id, result.get("topicVersionId")

    def test_04_read_parts(self, services, session):
        """Test READ Parts operatie (v3)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak en checkout topic
        create_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Lees parts
        result = services['parts'].get_parts(topic_id, topic_version_id)
        assert result is not None
        logger.info(f"✅ READ Parts: Parts gelezen voor {topic_id}")

    def test_05_update_part(self, services, session):
        """Test UPDATE Part operatie (v2)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak en checkout topic
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Update part
        result = services['parts'].update_part(
            topic_id,
            topic_version_id,
            "contentPart",
            {"text": "Updated content"}
        )
        
        assert result is not None
        logger.info(f"✅ UPDATE Part: Part bijgewerkt voor {topic_id}")

    def test_06_update_metadata(self, services, session):
        """Test UPDATE Metadata operatie (v2)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak en checkout topic
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Update metadata
        result = services['topic'].update_metadata(
            topic_id,
            topic_version_id,
            {"key": "value"}
        )
        
        assert result is not None
        logger.info(f"✅ UPDATE Metadata: Metadata bijgewerkt voor {topic_id}")

    def test_07_add_relation(self, services, session):
        """Test ADD Relation operatie (v2)."""
        topic_id_1 = str(uuid.uuid4())
        topic_id_2 = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        relation_type_id = "00000000-0000-0000-0000-000000000002"
        
        # Maak twee topics
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id_1,
                "topicTitle": "Test Topic 1",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id_2,
                "topicTitle": "Test Topic 2",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        # Checkout eerste topic
        checkout_result = services['checkout'].checkout(topic_id_1)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Voeg relatie toe
        result = services['relations'].add_relation(
            topic_id_1,
            topic_version_id,
            relation_type_id,
            [topic_id_2]
        )
        
        assert result is not None
        logger.info(f"✅ ADD Relation: Relatie toegevoegd van {topic_id_1} naar {topic_id_2}")

    def test_08_add_tag(self, services, session):
        """Test ADD Tag operatie (v2)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        hierarchy_topic_id = str(uuid.uuid4())
        hierarchy_node_id = str(uuid.uuid4())
        
        # Maak topic
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        # Checkout topic
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Voeg tag toe
        result = services['relations'].add_tag(
            topic_id,
            topic_version_id,
            hierarchy_topic_id,
            hierarchy_node_id
        )
        
        assert result is not None
        logger.info(f"✅ ADD Tag: Tag toegevoegd aan {topic_id}")

    def test_09_checkin_topic(self, services, session):
        """Test CHECKIN operatie (v4)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak en checkout topic
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Checkin topic
        result = services['checkout'].checkin(topic_id, topic_version_id)
        assert result is not None
        logger.info(f"✅ CHECKIN: Topic ingecheckt: {topic_id}")

    def test_10_delete_topic(self, services, session):
        """Test DELETE operatie (v3)."""
        topic_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak en checkout topic
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": topic_id,
                "topicTitle": "Test Topic",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        
        checkout_result = services['checkout'].checkout(topic_id)
        topic_version_id = checkout_result.get("topicVersionId")
        
        # Delete topic
        result = services['topic'].delete_topic(topic_id, topic_version_id)
        assert result is not None
        logger.info(f"✅ DELETE: Topic verwijderd: {topic_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
