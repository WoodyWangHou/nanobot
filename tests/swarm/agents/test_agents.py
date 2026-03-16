# Test agents
import pytest
from nanobot.swarm.agents.litellm_agent import LiteLLMAgent, create_litellm_agent


def test_litellm_agent_creation():
    agent = create_litellm_agent("test", "instructions", "gpt-4o")
    assert agent.name == "test"
    assert agent.model == "gpt-4o"


def test_litellm_agent_structure():
    agent = LiteLLMAgent(name="researcher", instructions="do research", model="minimax/MiniMax-M2.1")
    assert agent.name == "researcher"
    assert "research" in agent.instructions
    assert agent.model == "minimax/MiniMax-M2.1"


@pytest.mark.asyncio
async def test_litellm_agent_run():
    agent = LiteLLMAgent(name="test", instructions="You are a helpful assistant.", model="gpt-4o")
    # This will fail if no API key, but tests the structure
    try:
        result = await agent.run("Say hello")
        assert "final_output" in result
    except Exception as e:
        # Expected if no API key
        assert "Error" in str(e) or "authentication" in str(e).lower() or "api" in str(e).lower()
