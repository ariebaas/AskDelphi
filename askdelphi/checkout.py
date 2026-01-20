"""Checkout and checkin service for AskDelphi topics.

This module provides a small helper around the AskDelphiSession
to perform checkout and checkin operations on topics.
"""

from askdelphi.session import AskDelphiSession


class CheckoutService:
    """Service for handling topic checkout and checkin operations."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session

    def checkout(self, topic_id: str):
        """Checkout a topic for editing."""
        return self.session.post(f"/topics/{topic_id}/checkout", json={})

    def checkin(self, topic_id: str, comment: str = ""):
        """Checkin a topic after editing with an optional comment."""
        return self.session.post(
            f"/topics/{topic_id}/checkin", json={"comment": comment}
        )
