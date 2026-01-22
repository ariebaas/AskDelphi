"""Digital Coach importer die een gemapt topic tree in AskDelphi pusht.

Deze module coördineert het aanmaken of updaten van topics, checkout/checkin
en part updates met behulp van AskDelphiSession en helper services.
"""

import logging
from ..api_client.session import AskDelphiSession
from ..api_client.checkout import CheckoutService
from ..api_client.parts import PartService
from ..api_client.exceptions import AskDelphiAuthError
from .mapper import TopicNode
from .. import config
env_config = config.env

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

        # Maak of update topic aan
        result = self.session.post(f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic", json=payload)
        topic_version_id = result.get("topicVersionKey") or result.get("topicVersionId")
        logger.info(f"{indent}✓ Topic aangemaakt/bijgewerkt: {topic.title}")

        if not env_config.SKIP_CHECKOUT_CHECKIN:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Topic checkout")
            checkout_result = self.checkout.checkout(topic.id)
            topic_version_id = checkout_result.get("topicVersionId") or topic_version_id

            if env_config.DEBUG:
                logger.debug(f"{indent}  → Parts updaten")
            self._update_parts(topic, topic_version_id)

            if env_config.DEBUG:
                logger.debug(f"{indent}  → Topic checkin")
            self.checkout.checkin(topic.id, topic_version_id)
        else:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → Checkout/checkin overgeslagen (SKIP_CHECKOUT_CHECKIN=true)")
            self._update_parts(topic, topic_version_id)

        if topic.children:
            if env_config.DEBUG:
                logger.debug(f"{indent}  → {len(topic.children)} kind topic(s) verwerkt")
            for child in topic.children:
                self._import_topic_recursive(child, depth + 1)
        elif env_config.DEBUG:
            logger.debug(f"{indent}  → Geen kinderen om te verwerken")

    def _update_parts(self, topic: TopicNode, topic_version_id: str = None) -> None:
        """Update het contentPart voor een topic indien content aanwezig is."""
        if "content" in topic.metadata and topic_version_id:
            self.parts.update_part(
                topic.id,
                topic_version_id,
                "contentPart",
                {"text": topic.metadata["content"]},
            )
