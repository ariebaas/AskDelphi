"""Digital Coach importer die een gemapt topic tree in AskDelphi pusht.

Deze module coördineert het aanmaken of updaten van topics, checkout/checkin
en part updates met behulp van AskDelphiSession en helper services.
"""

import logging
from ..api_client.session import AskDelphiSession
from ..api_client.checkout import CheckoutService
from ..api_client.parts import PartService
from ..api_client.topic import TopicService
from ..api_client.relations import RelationService
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
        self.topic = TopicService(session)
        self.relations = RelationService(session)

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
            "topicId": topic.id,
            "topicTitle": topic.title,
            "topicTypeId": str(topic.topic_type["key"]),
            "topicTypeNamespace": topic.topic_type.get("namespace", "AskDelphi.DigitalCoach"),
            "copyParentTags": False,
            "language": "nl-NL",
        }
        
        # Add parentTopicId if this is not a root topic
        if topic.parent_id:
            payload["parentTopicId"] = topic.parent_id
            if env_config.DEBUG:
                logger.debug(f"{indent}  → parentTopicId: {topic.parent_id}")
            # Add parentTopicRelationTypeId if available in metadata
            if "parentTopicRelationTypeId" in topic.metadata:
                payload["parentTopicRelationTypeId"] = topic.metadata["parentTopicRelationTypeId"]
                if env_config.DEBUG:
                    logger.debug(f"{indent}  → parentTopicRelationTypeId: {topic.metadata['parentTopicRelationTypeId']}")
            elif env_config.DEBUG:
                logger.debug(f"{indent}  → parentTopicRelationTypeId: NOT in metadata")
        elif env_config.DEBUG:
            logger.debug(f"{indent}  → parent_id is empty/None")
        
        # Add description if available in metadata
        if "description" in topic.metadata and topic.metadata["description"]:
            payload["description"] = topic.metadata["description"]
        
        # Add tags if available
        if topic.tags:
            payload["tags"] = topic.tags if isinstance(topic.tags, list) else [topic.tags]

        if env_config.DEBUG:
            logger.debug(f"{indent}  Payload: {payload}")

        # Maak of update topic aan
        try:
            result = self.session.post(f"v4/tenant/{{tenantId}}/project/{{projectId}}/acl/{{aclEntryId}}/topic", json=payload)
        except Exception as e:
            logger.error(f"{indent}✗ Topic creatie mislukt: {topic.title}")
            logger.error(f"{indent}  Fout: {str(e)}")
            logger.error(f"{indent}  Payload: {payload}")
            raise
        topic_version_id = result.get("topicVersionKey") or result.get("topicVersionId")
        logger.info(f"{indent}✓ Topic aangemaakt/bijgewerkt: {topic.title}")

        # Checkout topic voor bewerking
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Topic checkout")
        checkout_result = self.checkout.checkout(topic.id)
        topic_version_id = checkout_result.get("topicVersionId") or topic_version_id

        # Update parts, metadata, relaties en tags
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Parts updaten")
        self._update_parts(topic, topic_version_id)

        if env_config.DEBUG:
            logger.debug(f"{indent}  → Metadata updaten")
        self._update_metadata(topic, topic_version_id)

        if env_config.DEBUG:
            logger.debug(f"{indent}  → Relaties toevoegen")
        self._add_relations(topic, topic_version_id)

        if env_config.DEBUG:
            logger.debug(f"{indent}  → Tags toevoegen")
        self._add_tags(topic, topic_version_id)

        # Checkin topic
        if env_config.DEBUG:
            logger.debug(f"{indent}  → Topic checkin")
        self.checkout.checkin(topic.id, topic_version_id)

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

    def _update_metadata(self, topic: TopicNode, topic_version_id: str = None) -> None:
        """Update metadata voor een topic."""
        if topic.metadata and topic_version_id:
            try:
                self.topic.update_metadata(
                    topic.id,
                    topic_version_id,
                    topic.metadata,
                )
            except Exception as e:
                if env_config.DEBUG:
                    logger.debug(f"Metadata update mislukt: {e}")

    def _add_relations(self, topic: TopicNode, topic_version_id: str = None) -> None:
        """Voeg relaties toe voor een topic."""
        if topic_version_id and hasattr(topic, 'relations') and topic.relations:
            try:
                for relation_type, target_ids in topic.relations.items():
                    if target_ids:
                        self.relations.add_relation(
                            topic.id,
                            topic_version_id,
                            relation_type,
                            target_ids,
                        )
            except Exception as e:
                if env_config.DEBUG:
                    logger.debug(f"Relatie toevoegen mislukt: {e}")

    def _add_tags(self, topic: TopicNode, topic_version_id: str = None) -> None:
        """Voeg tags toe voor een topic."""
        if topic_version_id and topic.tags:
            try:
                for tag in topic.tags:
                    if isinstance(tag, dict) and 'hierarchyTopicId' in tag and 'hierarchyNodeId' in tag:
                        self.relations.add_tag(
                            topic.id,
                            topic_version_id,
                            tag['hierarchyTopicId'],
                            tag['hierarchyNodeId'],
                        )
            except Exception as e:
                if env_config.DEBUG:
                    logger.debug(f"Tag toevoegen mislukt: {e}")

    def delete_topic_recursive(self, topic: TopicNode, topic_version_id: str = None) -> None:
        """Verwijder een topic en alle onderliggende topics (cascading delete).
        
        Dit zorgt ervoor dat:
        1. Alle onderliggende topics recursief worden verwijderd
        2. Relaties worden opgeruimd
        3. Bovenliggend topic wordt bijgewerkt
        """
        if not topic_version_id:
            logger.warning(f"Kan topic {topic.id} niet verwijderen zonder version ID")
            return
        
        indent = "  " * (self._get_depth(topic) + 1)
        
        # Verwijder eerst alle onderliggende topics
        if topic.children:
            if env_config.DEBUG:
                logger.debug(f"{indent}→ {len(topic.children)} onderliggende topic(s) verwijderen")
            
            for child in topic.children:
                # Haal child topic op om version ID te krijgen
                try:
                    child_topic = self.topic.get_topic(child.id)
                    if child_topic:
                        child_version_id = child_topic.get("topicVersionId") or child_topic.get("topicVersionKey")
                        if child_version_id:
                            self.delete_topic_recursive(child, child_version_id)
                except Exception as e:
                    if env_config.DEBUG:
                        logger.debug(f"{indent}  ⚠ Kon child topic {child.id} niet verwijderen: {e}")
        
        # Verwijder het topic zelf
        try:
            self.topic.delete_topic_recursive(
                topic.id,
                topic_version_id,
                [child.id for child in topic.children]
            )
            logger.info(f"{indent}✓ Topic verwijderd: {topic.title}")
        except Exception as e:
            logger.error(f"{indent}✗ Kon topic {topic.id} niet verwijderen: {e}")

    def _get_depth(self, topic: TopicNode, depth: int = 0) -> int:
        """Bereken de diepte van een topic in de hiërarchie."""
        if not topic.parent_id:
            return 0
        # Dit is een vereenvoudigde implementatie
        return depth
