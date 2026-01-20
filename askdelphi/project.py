"""Project management service for AskDelphi.

This module provides helper methods to create and retrieve projects
in AskDelphi using the AskDelphiSession client.
"""

from askdelphi.session import AskDelphiSession


class ProjectService:
    """Service for managing projects in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def create_project(self, project_id: str, title: str, description: str = ""):
        """Create a new project in AskDelphi."""
        return self.session.post(
            "/projects",
            json={"id": project_id, "title": title, "description": description},
        )

    def get_project(self, project_id: str):
        """Retrieve a project by its identifier."""
        return self.session.get(f"/projects/{project_id}")
