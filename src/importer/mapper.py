"""Mapper van generieke proces JSON naar interne topic tree.

Deze module vertaalt een hiërarchische proces definitie naar
een boom van TopicNode objecten die in AskDelphi kunnen worden geïmporteerd.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..config.topic_types import DEFAULT_TOPIC_TYPES
from .. import config
env_config = config.env

logger = logging.getLogger(__name__)


@dataclass
class TopicNode:
    """Vertegenwoordigt een topic in de Digital Coach structuur."""

    id: str
    title: str
    topic_type: Dict[str, Any]
    parent_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["TopicNode"] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class DigitalCoachMapper:
    """Map een proces JSON structuur naar een boom van TopicNode objecten."""

    def __init__(self) -> None:
        self.topic_types = {t["title"]: t for t in DEFAULT_TOPIC_TYPES}

    def map_process(self, process: dict) -> List[TopicNode]:
        """Map het root proces naar een lijst van root TopicNode objecten."""
        logger.info(f"Proces gemapt: {process.get('id')} - {process.get('title')}")
        if env_config.DEBUG:
            logger.debug(f"  Beschrijving: {process.get('description', 'N/A')}")
            logger.debug(f"  Tags: {process.get('tags', [])}")
        root_topic = self._map_homepage(process)
        logger.info(f"✓ Proces gemapt naar 1 root topic met {len(root_topic.children)} kinderen")
        return [root_topic]

    def _map_homepage(self, process: dict) -> TopicNode:
        """Maak het Digital Coach homepagina topic en zijn kinderen aan."""
        topic_type_name = process.get("topicType", "Digitale Coach Homepagina")
        home_type = self.topic_types.get(topic_type_name, self.topic_types["Digitale Coach Homepagina"])
        home = TopicNode(
            id=process.get("id", "dc-home"),
            title=process.get("title", "Digitale Coach"),
            topic_type=home_type,
            parent_id=None,
            metadata={
                "description": process.get("description", ""),
            },
            tags=process.get("tags", []),
        )

        for task in process.get("tasks", []):
            child = self._map_task(task, parent_id=home.id)
            home.children.append(child)

        for step in process.get("steps", []):
            child = self._map_step(step, parent_id=home.id)
            home.children.append(child)

        return home

    def _map_task(self, task: dict, parent_id: str) -> TopicNode:
        """Map een enkele taak en zijn stappen."""
        if env_config.DEBUG:
            logger.debug(f"  Taak gemapt: {task.get('id')} - {task.get('title')}")

        topic_type_name = task.get("topicType", "Task")
        task_type = self.topic_types.get(topic_type_name, self.topic_types.get("Task", self.topic_types["Digitale Coach Stap"]))
        node = TopicNode(
            id=task["id"],
            title=task["title"],
            topic_type=task_type,
            parent_id=parent_id,
            metadata={
                "description": task.get("description", ""),
            },
            tags=task.get("tags", []),
        )

        steps = task.get("steps", [])
        if env_config.DEBUG:
            logger.debug(f"    → {len(steps)} stap(pen) gemapt")

        for step in steps:
            step_node = self._map_step(step, parent_id=node.id)
            node.children.append(step_node)

        return node

    def _map_step(self, step: dict, parent_id: str) -> TopicNode:
        """Map een enkele proces stap en zijn instructies."""
        if env_config.DEBUG:
            logger.debug(f"      Stap gemapt: {step.get('id')} - {step.get('title')}")

        topic_type_name = step.get("topicType", "Digitale Coach Stap")
        step_type = self.topic_types.get(topic_type_name, self.topic_types["Digitale Coach Stap"])
        node = TopicNode(
            id=step["id"],
            title=step["title"],
            topic_type=step_type,
            parent_id=parent_id,
            metadata={
                "description": step.get("description", ""),
            },
            tags=step.get("tags", []),
        )

        instructions = step.get("instructions", [])
        if env_config.DEBUG:
            logger.debug(f"        → {len(instructions)} instructie(s) gemapt")

        for instr in instructions:
            instr_node = self._map_instruction(instr, parent_id=node.id)
            node.children.append(instr_node)

        return node

    def _map_instruction(self, instr: dict, parent_id: str) -> TopicNode:
        """Map een enkele instructie onder een stap."""
        if env_config.DEBUG:
            logger.debug(f"          Instructie gemapt: {instr.get('id')} - {instr.get('title')}")

        topic_type_name = instr.get("topicType", "Digitale Coach Instructie")
        instr_type = self.topic_types.get(topic_type_name, self.topic_types["Digitale Coach Instructie"])
        return TopicNode(
            id=instr["id"],
            title=instr["title"],
            topic_type=instr_type,
            parent_id=parent_id,
            metadata={
                "content": instr.get("content", ""),
            },
            tags=instr.get("tags", []),
        )
