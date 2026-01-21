"""Project management service voor AskDelphi.

Deze module biedt helper methoden om projecten aan te maken en op te halen
in AskDelphi met behulp van de AskDelphiSession client.
"""

from askdelphi.session import AskDelphiSession


class ProjectService:
    """Service voor het beheren van projecten in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def create_project(self, project_id: str, title: str, description: str = ""):
        """Maak een nieuw project aan in AskDelphi."""
        return self.session.post(
            "/projects",
            json={"id": project_id, "title": title, "description": description},
        )

    def get_project(self, project_id: str):
        """Haal een project op via zijn identifier."""
        return self.session.get(f"/projects/{project_id}")
