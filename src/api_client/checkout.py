"""Checkout en checkin service voor AskDelphi topics.

Deze module biedt een kleine helper rond AskDelphiSession
om checkout en checkin operaties op topics uit te voeren.
"""

from .session import AskDelphiSession


class CheckoutService:
    """Service voor het afhandelen van topic checkout en checkin operaties."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def checkout(self, topic_id: str):
        """Checkout een topic voor bewerking."""
        endpoint = f"v3/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/workflowstate"
        return self.session.post(endpoint, json={"workflowAction": "CheckOut"})

    def checkin(self, topic_id: str, comment: str = ""):
        """Checkin een topic na bewerking met een optioneel commentaar."""
        endpoint = f"v3/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic/{topic_id}/workflowstate"
        return self.session.post(
            endpoint, json={"workflowAction": "CheckIn", "comment": comment}
        )
