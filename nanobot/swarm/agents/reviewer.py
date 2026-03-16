# Reviewer agent for analyzing results
from typing import Optional

try:
    from agents import Agent
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    Agent = None


def create_reviewer_agent(model: str = "gpt-4o") -> Optional["Agent"]:
    """Create a reviewer agent for analyzing results."""
    if not AGENTS_SDK_AVAILABLE:
        return None

    return Agent(
        name="reviewer",
        instructions="""You are a review agent that analyzes experiment results.

        Your task:
        1. Compare results to success criteria
        2. Identify patterns in successes/failures
        3. Provide actionable feedback for improvement

        Be constructive and specific.""",
        handoff_description="An agent for reviewing results",
        model=model
    )
