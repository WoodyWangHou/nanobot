# Executor agent for running experiments
from typing import Optional

try:
    from agents import Agent
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    Agent = None


def create_executor_agent(model: str = "gpt-4o") -> Optional["Agent"]:
    """Create an executor agent for running experiments."""
    if not AGENTS_SDK_AVAILABLE:
        return None

    return Agent(
        name="executor",
        instructions="""You are an execution agent that runs experiments
        based on research findings.

        Your task:
        1. Execute the assigned task
        2. Validate outputs against success criteria
        3. Return results with metrics

        Be thorough and report all outcomes.""",
        handoff_description="An agent for running experiments",
        model=model
    )
