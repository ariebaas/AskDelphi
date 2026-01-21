"""Digital Coach importer that pushes a mapped topic tree into AskDelphi.

This module coordinates the creation or update of topics, checkout/checkin
and part updates using the AskDelphiSession and helper services.
"""

import logging
from askdelphi.session import AskDelphiSession
from askdelphi.checkout import CheckoutService
from askdelphi.parts import PartService
from askdelphi.exceptions import AskDelphiAuthError
from importer.mapper import TopicNode
import config.env as env_config

logger = logging.getLogger(__name__)


class DigitalCoachImporter:
    """Import a Digital Coach topic tree into AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session
        self.checkout = CheckoutService(session)
        self.parts = PartService(session)

    def import_topics(self, root_topics: list[TopicNode]) -> None:
        """Import all root topics and their descendants."""
        logger.info(f"Starting import of {len(root_topics)} root topic(s)")
        for topic in root_topics:
            self._import_topic_recursive(topic)
        logger.info("Import completed successfully")

    def _import_topic_recursive(self, topic: TopicNode, depth: int = 0) -> None:
        """Create or update a single topic and recurse into its children."""
        indent = "  " * depth
        
        if env_config.DEBUG:
            logger.debug(f"{indent}[IMPORT] Processing topic: {topic.id}")
            logger.debug(f"{indent}  Title: {topic.title}")
            logger.debug(f"{indent}  Type: {topic.topic_type.get('title', 'Unknown')}")
            logger.debug(f"{indent}  Parent: {topic.parent_id}")
            logger.debug(f"{indent}  Children: {len(topic.children)}")
            logger.debug(f"{indent}  Tags: {topic.tags}")
            logger.debug(f"{indent}  Metadata keys: {list(topic.metadata.keys())}")
        
        # Build relations object with children IDs
        relations = {
            "parent": topic.parent_id,
            "children": [child.id for child in topic.children],
            "related": []
        }
        
        payload = {
            "id": topic.id,
            "title": topic.title,
            "topicTypeKey": str(topic.topic_type["key"]),
            "topicTypeNamespace": topic.topic_type["namespace"],
            "parentId": topic.parent_id,
            "metadata": topic.metadata,
            "tags": topic.tags,
            "relations": relations,
        }

        try:
            # Try to see if topic exists
            self.session.get(f"/topics/{topic.id}")
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Updating existing topic")
            # Update existing
            self.session.put(f"/topics/{topic.id}", json=payload)
            logger.info(f"{indent}✓ Updated topic: {topic.title}")
        except AskDelphiAuthError:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Creating new topic")
            # Create new
            self.session.post("/topics", json=payload)
            logger.info(f"{indent}✓ Created topic: {topic.title}")

        # Checkout, update parts, checkin
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Checkout topic")
        self.checkout.checkout(topic.id)
        
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Update parts")
        self._update_parts(topic)
        
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Checkin topic")
        self.checkout.checkin(topic.id, comment="Automated Digital Coach import")

        # Process children
        if topic.children:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Processing {len(topic.children)} child topic(s)")
            for child in topic.children:
                self._import_topic_recursive(child, depth + 1)
        elif env_config.DEBUG:
            logger.debug(f"{indent}  → No children to process")

    def _update_parts(self, topic: TopicNode) -> None:
        """Update the contentPart for a topic if content is present."""
        if "content" in topic.metadata:
            self.parts.update_part(
                topic.id,
                "contentPart",
                {"text": topic.metadata["content"]},
            )
