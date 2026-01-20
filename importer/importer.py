"""Digital Coach importer that pushes a mapped topic tree into AskDelphi.

This module coordinates the creation or update of topics, checkout/checkin
and part updates using the AskDelphiSession and helper services.
"""

from askdelphi.session import AskDelphiSession
from askdelphi.checkout import CheckoutService
from askdelphi.parts import PartService
from askdelphi.exceptions import AskDelphiAuthError
from importer.mapper import TopicNode


class DigitalCoachImporter:
    """Import a Digital Coach topic tree into AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session
        self.checkout = CheckoutService(session)
        self.parts = PartService(session)

    def import_topics(self, root_topics: list[TopicNode]) -> None:
        """Import all root topics and their descendants."""
        for topic in root_topics:
            self._import_topic_recursive(topic)

    def _import_topic_recursive(self, topic: TopicNode) -> None:
        """Create or update a single topic and recurse into its children."""
        payload = {
            "id": topic.id,
            "title": topic.title,
            "topicTypeKey": str(topic.topic_type["key"]),
            "topicTypeNamespace": topic.topic_type["namespace"],
            "parentId": topic.parent_id,
            "metadata": topic.metadata,
            "tags": topic.tags,
        }

        try:
            # Try to see if topic exists
            self.session.get(f"/topics/{topic.id}")
            # Update existing
            self.session.put(f"/topics/{topic.id}", json=payload)
        except AskDelphiAuthError:
            # Create new
            self.session.post("/topics", json=payload)

        # Checkout, update parts, checkin
        self.checkout.checkout(topic.id)
        self._update_parts(topic)
        self.checkout.checkin(topic.id, comment="Automated Digital Coach import")

        for child in topic.children:
            self._import_topic_recursive(child)

    def _update_parts(self, topic: TopicNode) -> None:
        """Update the contentPart for a topic if content is present."""
        if "content" in topic.metadata:
            self.parts.update_part(
                topic.id,
                "contentPart",
                {"text": topic.metadata["content"]},
            )
