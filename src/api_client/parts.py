"""Part management service voor AskDelphi topics.

Deze module biedt helper methoden om parts (bijv. contentPart)
geassocieerd met een topic in AskDelphi te beheren.
"""

from .session import AskDelphiSession


class PartService:
    """Service voor het beheren van topic parts in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def get_parts(self, topic_id: str):
        """Haal alle parts op voor een gegeven topic."""
        return self.session.get(f"/topics/{topic_id}/parts")

    def create_part(self, topic_id: str, name: str, content: dict):
        """Maak een nieuw part aan voor een topic."""
        return self.session.post(
            f"/topics/{topic_id}/parts",
            json={"name": name, "content": content},
        )

    def update_part(self, topic_id: str, name: str, content: dict):
        """Update een bestaand part voor een topic."""
        return self.session.put(
            f"/topics/{topic_id}/parts/{name}",
            json={"name": name, "content": content},
        )
