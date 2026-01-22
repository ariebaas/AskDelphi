"""Part management service voor AskDelphi topics.

Deze module biedt helper methoden om parts (bijv. contentPart)
geassocieerd met een topic in AskDelphi te beheren.
"""

from .session import AskDelphiSession


class PartService:
    """Service voor het beheren van topic parts in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def get_parts(self, topic_id: str, topic_version_id: str):
        """Haal alle parts op voor een gegeven topic."""
        endpoint = f"v3/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/part"
        return self.session.get(endpoint)

    def create_part(self, topic_id: str, topic_version_id: str, name: str, content: dict):
        """Maak een nieuw part aan voor een topic."""
        endpoint = f"v3/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/part"
        return self.session.post(
            endpoint,
            json={"name": name, "content": content},
        )

    def update_part(self, topic_id: str, topic_version_id: str, name: str, content: dict):
        """Update een bestaand part voor een topic."""
        endpoint = f"v2/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/part/{name}"
        return self.session.put(
            endpoint,
            json={"part": content},
        )
