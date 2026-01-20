"""Part management service for AskDelphi topics.

This module provides helper methods to manage parts (e.g. contentPart)
associated with a topic in AskDelphi.
"""

from askdelphi.session import AskDelphiSession


class PartService:
    """Service for managing topic parts in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def get_parts(self, topic_id: str):
        """Retrieve all parts for a given topic."""
        return self.session.get(f"/topics/{topic_id}/parts")

    def create_part(self, topic_id: str, name: str, content: dict):
        """Create a new part for a topic."""
        return self.session.post(
            f"/topics/{topic_id}/parts",
            json={"name": name, "content": content},
        )

    def update_part(self, topic_id: str, name: str, content: dict):
        """Update an existing part for a topic."""
        return self.session.put(
            f"/topics/{topic_id}/parts/{name}",
            json={"name": name, "content": content},
        )
