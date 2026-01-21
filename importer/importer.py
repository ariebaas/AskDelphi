"""Digital Coach importer die een gemapt topic tree in AskDelphi pusht.

Deze module coördineert het aanmaken of updaten van topics, checkout/checkin
en part updates met behulp van AskDelphiSession en helper services.
"""

import logging
from api_client.session import AskDelphiSession
from api_client.checkout import CheckoutService
from api_client.parts import PartService
from api_client.exceptions import AskDelphiAuthError
from importer.mapper import TopicNode
import config.env as env_config

logger = logging.getLogger(__name__)


class DigitalCoachImporter:
    """Importeer een Digital Coach topic tree in AskDelphi."""

    def __init__(self, session: AskDelphiSession) -> None:
        self.session = session
        self.checkout = CheckoutService(session)
        self.parts = PartService(session)

    def import_topics(self, root_topics: list[TopicNode]) -> None:
        """Importeer alle root topics en hun afstammelingen."""
        logger.info(f"Import gestart van {len(root_topics)} root topic(s)")
        for topic in root_topics:
            self._import_topic_recursive(topic)
        logger.info("Import succesvol voltooid")

    def _import_topic_recursive(self, topic: TopicNode, depth: int = 0) -> None:
        """Maak of update een enkel topic aan en recurse in zijn kinderen."""
        indent = "  " * depth

        if env_config.DEBUG:
            logger.debug(f"{indent}[IMPORT] Topic verwerkt: {topic.id}")
            logger.debug(f"{indent}  Titel: {topic.title}")
            logger.debug(f"{indent}  Type: {topic.topic_type.get('title', 'Onbekend')}")
            logger.debug(f"{indent}  Parent: {topic.parent_id}")
            logger.debug(f"{indent}  Kinderen: {len(topic.children)}")
            logger.debug(f"{indent}  Tags: {topic.tags}")
            logger.debug(f"{indent}  Metadata sleutels: {list(topic.metadata.keys())}")

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
            self.session.get(f"/topics/{topic.id}")
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Bestaand topic updaten")
            self.session.put(f"/topics/{topic.id}", json=payload)
            logger.info(f"{indent}✓ Topic bijgewerkt: {topic.title}")
        except AskDelphiAuthError:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Nieuw topic aanmaken")
            self.session.post("/topics", json=payload)
            logger.info(f"{indent}✓ Topic aangemaakt: {topic.title}")

        if not env_config.SKIP_CHECKOUT_CHECKIN:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Topic checkout")
            self.checkout.checkout(topic.id)

            if env_config.DEBUG:
                logger.debug(f"{indent}  → Parts updaten")
            self._update_parts(topic)

            if env_config.DEBUG:
                logger.debug(f"{indent}  → Topic checkin")
            self.checkout.checkin(topic.id, comment="Geautomatiseerde Digital Coach import")
        else:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Checkout/checkin overgeslagen (SKIP_CHECKOUT_CHECKIN=true)")
            self._update_parts(topic)

        if topic.children:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → {len(topic.children)} kind topic(s) verwerkt")
            for child in topic.children:
                self._import_topic_recursive(child, depth + 1)
        elif env_config.DEBUG:
            logger.debug(f"{indent}  → Geen kinderen om te verwerken")

    def _update_parts(self, topic: TopicNode) -> None:
        """Update het contentPart voor een topic indien content aanwezig is."""
        if "content" in topic.metadata:
            self.parts.update_part(
                topic.id,
                "contentPart",
                {"text": topic.metadata["content"]},
            )
