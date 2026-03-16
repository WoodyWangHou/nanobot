# Researcher agent for exploring solutions
from typing import Optional

# Try to import OpenAI Agents SDK, fallback to LiteLLM if not available
try:
    from agents import Agent
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    Agent = None


def create_researcher_agent(model: str = "gpt-4o") -> Optional["Agent"]:
    """Create a researcher agent for exploring alternatives."""
    if not AGENTS_SDK_AVAILABLE:
        return None

    return Agent(
        name="researcher",
        instructions="""You are a research agent specialized in finding
        solutions through web searches, academic research, and data exploration.

        Your task:
        1. Search for relevant information
        2. Explore multiple approaches
        3. Provide structured findings with sources

        Always cite your sources and provide actionable insights.""",
        handoff_description="A research agent for exploring solutions",
        model=model
    )
