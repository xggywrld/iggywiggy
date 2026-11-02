"""Course content registry: the ordered list of topics and lookup helpers."""

from __future__ import annotations

from . import (t01_basics, t02_operators, t03_control_flow, t04_functions,
               t05_data_types, t06_files, t07_sql, t08_data_prep, t09_descriptive,
               t10_visualisation)
from .models import Item, Topic
from .projects import PROJECTS, get_project, prelude_for

__all__ = ["TOPICS", "PROJECTS", "get_topic", "get_item", "get_project", "prelude_for",
           "all_items", "all_tags"]

TOPICS: tuple[Topic, ...] = tuple(
    m.TOPIC for m in (t01_basics, t02_operators, t03_control_flow, t04_functions,
                      t05_data_types, t06_files, t07_sql, t08_data_prep,
                      t09_descriptive, t10_visualisation)
)

_TOPIC_BY_ID = {t.id: t for t in TOPICS}
_ITEM_INDEX: dict[str, tuple[Topic, Item]] = {
    item.id: (topic, item) for topic in TOPICS for item in topic.items
}


def get_topic(topic_id: str) -> Topic:
    return _TOPIC_BY_ID[topic_id]


def get_item(item_id: str) -> tuple[Topic, Item]:
    """Return ``(topic, item)`` for a global item id."""
    return _ITEM_INDEX[item_id]


def all_items() -> list[Item]:
    return [i for t in TOPICS for i in t.items]


def all_tags() -> list[str]:
    return sorted({tag for i in all_items() for tag in i.tags})
