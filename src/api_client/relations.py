"""Relations en tags service voor AskDelphi topics.

Deze module biedt helper methoden om relaties en tags
aan topics toe te voegen.
"""

from .session import AskDelphiSession


class RelationService:
    """Service voor het beheren van topic relaties en tags in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def add_relation(self, topic_id: str, topic_version_id: str, relation_type_id: str, target_topic_ids: list):
        """Voeg een relatie toe van dit topic naar andere topics."""
        endpoint = f"v2/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/relation"
        return self.session.post(
            endpoint,
            json={
                "relationTypeId": relation_type_id,
                "sourceTopicId": topic_id,
                "targetTopicIds": target_topic_ids,
            },
        )

    def add_tag(self, topic_id: str, topic_version_id: str, hierarchy_topic_id: str, hierarchy_node_id: str):
        """Voeg een tag toe aan een topic."""
        endpoint = f"v2/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/topicVersion/{topic_version_id}/tag"
        return self.session.post(
            endpoint,
            json={
                "tags": [
                    {
                        "hierarchyTopicId": hierarchy_topic_id,
                        "hierarchyNodeId": hierarchy_node_id,
                    }
                ]
            },
        )
