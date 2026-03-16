# Test event system
import pytest
from nanobot.swarm.storage.events import EventBus


def test_event_emission():
    bus = EventBus()
    received = []
    bus.subscribe("iteration_complete", lambda e: received.append(e))
    bus.publish("iteration_complete", {"id": 1, "result": "test"})
    assert len(received) == 1
    assert received[0]["id"] == 1


def test_multiple_subscribers():
    bus = EventBus()
    received1 = []
    received2 = []

    def callback1(e):
        received1.append(e)

    def callback2(e):
        received2.append(e)

    bus.subscribe("test_event", callback1)
    bus.subscribe("test_event", callback2)
    bus.publish("test_event", {"data": "value"})

    assert len(received1) == 1
    assert len(received2) == 1


def test_unsubscribe():
    bus = EventBus()
    received = []

    def callback(e):
        received.append(e)

    bus.subscribe("test_event", callback)
    bus.publish("test_event", {"data": "first"})
    bus.unsubscribe("test_event", callback)
    bus.publish("test_event", {"data": "second"})

    assert len(received) == 1
