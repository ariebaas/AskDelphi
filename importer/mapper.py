"""Mapper from generic process JSON into internal topic tree.

This module translates a hierarchical process definition into
a tree of TopicNode objects that can be imported into AskDelphi.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from config.topic_types import DEFAULT_TOPIC_TYPES


@dataclass
class TopicNode:
    """Represents a topic in the Digital Coach structure."""

    id: str
    title: str
    topic_type: Dict[str, Any]
    parent_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["TopicNode"] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class DigitalCoachMapper:
    """Map a process JSON structure into a tree of TopicNode objects."""

    def __init__(self) -> None:
        # Index topic types by title
        self.topic_types = {t["title"]: t for t in DEFAULT_TOPIC_TYPES}

    def map_process(self, process: dict) -> List[TopicNode]:
        """Map the root process into a list of root TopicNode objects."""
        root_topic = self._map_homepage(process)
        return [root_topic]

    def _map_homepage(self, process: dict) -> TopicNode:
        """Create the Digital Coach homepage topic and its children."""
        # Use specified topic type or default to Digitale Coach Homepagina
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

        # Support both tasks and steps
        for task in process.get("tasks", []):
            child = self._map_task(task, parent_id=home.id)
            home.children.append(child)

        for step in process.get("steps", []):
            child = self._map_step(step, parent_id=home.id)
            home.children.append(child)

        return home

    def _map_task(self, task: dict, parent_id: str) -> TopicNode:
        """Map a single task and its steps."""
        # Use specified topic type or default to Task
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

        for step in task.get("steps", []):
            step_node = self._map_step(step, parent_id=node.id)
            node.children.append(step_node)

        return node

    def _map_step(self, step: dict, parent_id: str) -> TopicNode:
        """Map a single process step and its instructions."""
        # Use specified topic type or default to Digitale Coach Stap
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

        for instr in step.get("instructions", []):
            instr_node = self._map_instruction(instr, parent_id=node.id)
            node.children.append(instr_node)

        return node

    def _map_instruction(self, instr: dict, parent_id: str) -> TopicNode:
        """Map a single instruction under a step."""
        # Use specified topic type or default to Digitale Coach Instructie
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
