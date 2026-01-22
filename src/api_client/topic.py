"""Topic management service voor AskDelphi topics.

Deze module biedt helper methoden om topic operaties
(READ, UPDATE Metadata, DELETE) uit te voeren, inclusief
cascading delete voor hiërarchische topics.
"""

import logging
from .session import AskDelphiSession

logger = logging.getLogger(__name__)


class TopicService:
    """Service voor het beheren van topics in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def get_topic(self, topic_id: str):
        """Haal een topic op met gegeven ID."""
        endpoint = f"v1/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}"
        return self.session.get(endpoint)

    def update_metadata(self, topic_id: str, topic_version_id: str, metadata: dict):
        """Update metadata voor een topic."""
        endpoint = f"v2/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/topicversionmetadata"
        return self.session.put(
            endpoint,
            json={"data": metadata},
        )

    def delete_topic(self, topic_id: str, topic_version_id: str):
        """Verwijder een topic (markeer als verwijderd)."""
        endpoint = f"v3/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}"
        return self.session.delete(endpoint)

    def delete_topic_recursive(self, topic_id: str, topic_version_id: str, children_ids: list = None):
        """Verwijder een topic en alle onderliggende topics (cascading delete).
        
        Args:
            topic_id: Topic ID om te verwijderen
            topic_version_id: Topic version ID
            children_ids: Lijst van onderliggende topic IDs (optioneel)
            
        Returns:
            Result van delete operatie
        """
        # Verwijder eerst alle onderliggende topics
        if children_ids:
            for child_id in children_ids:
                try:
                    # Haal child topic op om version ID te krijgen
                    child_topic = self.get_topic(child_id)
                    if child_topic:
                        child_version_id = child_topic.get("topicVersionId") or child_topic.get("topicVersionKey")
                        if child_version_id:
                            # Recursieve delete van child
                            self.delete_topic_recursive(
                                child_id,
                                child_version_id,
                                child_topic.get("children", [])
                            )
                except Exception as e:
                    logger.warning(f"Kon child topic {child_id} niet verwijderen: {e}")
        
        # Verwijder het topic zelf
        try:
            result = self.delete_topic(topic_id, topic_version_id)
            logger.info(f"Topic verwijderd: {topic_id}")
            return result
        except Exception as e:
            logger.error(f"Kon topic {topic_id} niet verwijderen: {e}")
            raise
