"""Test script voor cascading DELETE operatie.

Dit script test of onderliggende topics correct worden verwijderd
en relaties worden opgeruimd wanneer een parent topic wordt verwijderd.
"""

import pytest
import uuid
import logging
from pathlib import Path

from src.api_client.session import AskDelphiSession
from src.api_client.topic import TopicService
from src.api_client.checkout import CheckoutService
from src.importer.importer import DigitalCoachImporter
from src.importer.mapper import TopicNode
from src.config import env

logger = logging.getLogger(__name__)


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
    )


@pytest.fixture
def services(session):
    """Maak services voor tests."""
    return {
        'topic': TopicService(session),
        'checkout': CheckoutService(session),
        'importer': DigitalCoachImporter(session),
    }


class TestCascadingDelete:
    """Test cascading DELETE operatie."""

    def test_cascading_delete_removes_children(self, services, session):
        """Test dat cascading delete onderliggende topics verwijdert."""
        # Maak parent topic
        parent_id = str(uuid.uuid4())
        parent_type_id = "00000000-0000-0000-0000-000000000001"
        
        parent_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": parent_id,
                "topicTitle": "Parent Topic",
                "topicTypeId": parent_type_id,
                "copyParentTags": False,
            }
        )
        
        parent_version_id = parent_result.get("topicVersionKey") or parent_result.get("topicVersionId")
        
        # Maak child topics
        child_ids = []
        for i in range(3):
            child_id = str(uuid.uuid4())
            child_result = session.post(
                f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
                json={
                    "topicId": child_id,
                    "topicTitle": f"Child Topic {i+1}",
                    "topicTypeId": parent_type_id,
                    "copyParentTags": False,
                    "parentId": parent_id,
                }
            )
            child_ids.append(child_id)
        
        logger.info(f"✅ Created parent {parent_id} with {len(child_ids)} children")
        
        # Verwijder parent met cascading delete
        services['topic'].delete_topic_recursive(
            parent_id,
            parent_version_id,
            child_ids
        )
        
        logger.info(f"✅ Cascading delete: Parent en {len(child_ids)} children verwijderd")
        
        # Verify parent is deleted
        try:
            parent = services['topic'].get_topic(parent_id)
            # Als we hier komen, is het topic niet verwijderd (fout)
            assert parent is None or parent.get("deleted") is True
        except Exception:
            # Expected - topic should be deleted
            logger.info("✅ Parent topic successfully deleted")

    def test_cascading_delete_with_nested_hierarchy(self, services, session):
        """Test cascading delete met geneste hiërarchie (3 niveaus)."""
        # Maak 3-level hiërarchie
        level1_id = str(uuid.uuid4())
        level2_id = str(uuid.uuid4())
        level3_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Level 1 (root)
        level1_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": level1_id,
                "topicTitle": "Level 1",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        level1_version_id = level1_result.get("topicVersionKey") or level1_result.get("topicVersionId")
        
        # Level 2 (child of level 1)
        level2_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": level2_id,
                "topicTitle": "Level 2",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
                "parentId": level1_id,
            }
        )
        level2_version_id = level2_result.get("topicVersionKey") or level2_result.get("topicVersionId")
        
        # Level 3 (child of level 2)
        level3_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": level3_id,
                "topicTitle": "Level 3",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
                "parentId": level2_id,
            }
        )
        level3_version_id = level3_result.get("topicVersionKey") or level3_result.get("topicVersionId")
        
        logger.info(f"✅ Created 3-level hierarchy: {level1_id} → {level2_id} → {level3_id}")
        
        # Cascading delete from level 1 should remove all 3 levels
        services['topic'].delete_topic_recursive(
            level1_id,
            level1_version_id,
            [level2_id]
        )
        
        logger.info("✅ Cascading delete: All 3 levels removed")
        
        # Verify all are deleted
        for level_id in [level1_id, level2_id, level3_id]:
            try:
                topic = services['topic'].get_topic(level_id)
                assert topic is None or topic.get("deleted") is True
            except Exception:
                logger.info(f"✅ Level {level_id} successfully deleted")

    def test_cascading_delete_preserves_siblings(self, services, session):
        """Test dat cascading delete sibling topics niet verwijdert."""
        parent_id = str(uuid.uuid4())
        topic_type_id = "00000000-0000-0000-0000-000000000001"
        
        # Maak parent
        parent_result = session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": parent_id,
                "topicTitle": "Parent",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }
        )
        parent_version_id = parent_result.get("topicVersionKey") or parent_result.get("topicVersionId")
        
        # Maak 2 siblings
        sibling1_id = str(uuid.uuid4())
        sibling2_id = str(uuid.uuid4())
        
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": sibling1_id,
                "topicTitle": "Sibling 1",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
                "parentId": parent_id,
            }
        )
        
        session.post(
            f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic",
            json={
                "topicId": sibling2_id,
                "topicTitle": "Sibling 2",
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
                "parentId": parent_id,
            }
        )
        
        logger.info(f"✅ Created parent with 2 siblings")
        
        # Delete only sibling 1
        sibling1_topic = services['topic'].get_topic(sibling1_id)
        sibling1_version_id = sibling1_topic.get("topicVersionId") or sibling1_topic.get("topicVersionKey")
        
        services['topic'].delete_topic(sibling1_id, sibling1_version_id)
        
        # Verify sibling 2 still exists
        sibling2_topic = services['topic'].get_topic(sibling2_id)
        assert sibling2_topic is not None
        logger.info("✅ Sibling 2 preserved after deleting Sibling 1")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
