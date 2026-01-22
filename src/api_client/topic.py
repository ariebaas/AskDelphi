"""Topic management service voor AskDelphi topics.

Deze module biedt helper methoden om topic operaties
(READ, UPDATE Metadata, DELETE) uit te voeren.
"""

from .session import AskDelphiSession


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
