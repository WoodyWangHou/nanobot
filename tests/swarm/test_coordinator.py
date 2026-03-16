# Test coordinator
import pytest
from nanobot.swarm.coordinator import SwarmCoordinator
from nanobot.swarm.storage.models import BudgetPolicy
from nanobot.swarm.storage.database import Database


def test_coordinator_creation():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    coordinator = SwarmCoordinator(db, policy)
    assert coordinator is not None


def test_coordinator_status():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    coordinator = SwarmCoordinator(db, policy)

    status = coordinator.get_status()
    assert status["status"] == "no_experiment"


def test_coordinator_litellm_fallback():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    # Use a model that requires LiteLLM
    coordinator = SwarmCoordinator(db, policy, model="minimax/MiniMax-M2.1")

    assert coordinator._use_litellm == True
    assert "researcher" in coordinator._agents
    assert "executor" in coordinator._agents
    assert "reviewer" in coordinator._agents


def test_experiment_lifecycle():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    coordinator = SwarmCoordinator(db, policy)

    import asyncio
    exp = asyncio.run(coordinator.start_experiment("test goal", "success criteria"))

    assert exp.id is not None
    assert exp.goal == "test goal"
    assert exp.status == "running"

    status = coordinator.get_status()
    assert status["status"] == "running"
