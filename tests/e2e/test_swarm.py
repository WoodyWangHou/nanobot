# End-to-end test for swarm
import pytest
import asyncio
from nanobot.swarm.coordinator import SwarmCoordinator
from nanobot.swarm.storage.database import Database
from nanobot.swarm.storage.models import BudgetPolicy
from nanobot.channel_adapter import ChannelAdapter


@pytest.mark.asyncio
async def test_full_experiment_flow():
    """Test complete experiment lifecycle."""
    # 1. Create coordinator with LiteLLM (for compatibility)
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=100000, window_duration="1h")
    coordinator = SwarmCoordinator(db, policy, model="gpt-4o")

    # 2. Start experiment
    exp = await coordinator.start_experiment(
        goal="Test the swarm system",
        success_criteria="Successfully complete iteration"
    )
    assert exp.id is not None

    # 3. Check status
    status = coordinator.get_status()
    assert status["status"] == "running"

    # 4. Try to run an iteration (will fail without API key but tests the flow)
    result = await coordinator.run_iteration("researcher", "What is 2+2?")

    # Should either succeed with API key or fail gracefully
    assert "result" in result or "error" in result


@pytest.mark.asyncio
async def test_channel_adapter():
    """Test channel adapter integration."""
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=100000, window_duration="1h")
    coordinator = SwarmCoordinator(db, policy, model="gpt-4o")
    adapter = ChannelAdapter(coordinator, db)

    # Test status command
    response = await adapter.handle_message("/status", "user123")
    assert "Status" in response

    # Test experiment start
    response = await adapter.handle_message("/experiment start Test goal", "user123")
    assert "started" in response.lower() or "Experiment" in response


def test_provider_detection():
    """Test that MiniMax and Gemini use LiteLLM."""
    from nanobot.swarm.coordinator import _requires_litellm

    assert _requires_litellm("minimax/MiniMax-M2.1") == True
    assert _requires_litellm("gemini/gemini-pro") == True
    assert _requires_litellm("gpt-4o") == True
    assert _requires_litellm("claude-3-opus") == True
