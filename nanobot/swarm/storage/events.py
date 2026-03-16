# Event system for progress tracking
from typing import Callable, Dict, List
from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable):
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: dict):
        for callback in self._subscribers[event_type]:
            callback(data)

    def unsubscribe(self, event_type: str, callback: Callable):
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
