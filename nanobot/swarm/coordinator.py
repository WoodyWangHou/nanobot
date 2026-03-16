# Swarm coordinator for agent orchestration
from typing import Optional, Dict, Any, Union
from .storage.database import Database
from .storage.models import BudgetPolicy, Experiment
from .storage.events import EventBus
from .controller.budget import BudgetController
from .controller.pacer import Pacer

# Try to import Agents SDK
try:
    from agents import Agent, Runner
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    Agent = None
    Runner = None


# Models that require LiteLLM (not supported by OpenAI Agents SDK)
LITELLM_ONLY_MODELS = ("minimax/", "gemini/", "claude/", "gpt-", "deepseek", "qwen", "kimi")


def _requires_litellm(model: str) -> bool:
    """Check if model requires LiteLLM fallback."""
    model_lower = model.lower()
    return any(model_lower.startswith(m.replace("/", "")) or m in model_lower for m in LITELLM_ONLY_MODELS)


class SwarmCoordinator:
    def __init__(self, db: Database, budget_policy: BudgetPolicy, model: str = "gpt-4o"):
        self.db = db
        self.budget = BudgetController(budget_policy)
        self.pacer = Pacer()
        self.events = EventBus()
        self._current_experiment: Optional[Experiment] = None
        self.model = model
        self._agents: Dict[str, Any] = {}
        self._use_litellm = not AGENTS_SDK_AVAILABLE or _requires_litellm(model)

        # Subscribe to events
        self.events.subscribe("iteration_complete", self._on_iteration_complete)

        # Initialize agents
        self._init_agents()

    def _init_agents(self):
        """Initialize agents using OpenAI Agents SDK or LiteLLM fallback."""
        if self._use_litellm:
            self._init_litellm_agents()
        elif AGENTS_SDK_AVAILABLE:
            self._init_sdk_agents()

    def _init_sdk_agents(self):
        """Initialize agents using OpenAI Agents SDK."""
        from .agents.researcher import create_researcher_agent
        from .agents.executor import create_executor_agent
        from .agents.reviewer import create_reviewer_agent

        self._agents["researcher"] = create_researcher_agent(self.model)
        self._agents["executor"] = create_executor_agent(self.model)
        self._agents["reviewer"] = create_reviewer_agent(self.model)

    def _init_litellm_agents(self):
        """Initialize agents using LiteLLM (supports MiniMax, Gemini, etc.)."""
        from .agents.litellm_agent import create_litellm_agent

        researcher_instructions = """You are a research agent specialized in finding
        solutions through web searches, academic research, and data exploration.

        Your task:
        1. Search for relevant information
        2. Explore multiple approaches
        3. Provide structured findings with sources

        Always cite your sources and provide actionable insights."""

        executor_instructions = """You are an execution agent that runs experiments
        based on research findings.

        Your task:
        1. Execute the assigned task
        2. Validate outputs against success criteria
        3. Return results with metrics

        Be thorough and report all outcomes."""

        reviewer_instructions = """You are a review agent that analyzes experiment results.

        Your task:
        1. Compare results to success criteria
        2. Identify patterns in successes/failures
        3. Provide actionable feedback for improvement

        Be constructive and specific."""

        self._agents["researcher"] = create_litellm_agent("researcher", researcher_instructions, self.model)
        self._agents["executor"] = create_litellm_agent("executor", executor_instructions, self.model)
        self._agents["reviewer"] = create_litellm_agent("reviewer", reviewer_instructions, self.model)

    async def start_experiment(self, goal: str, success_criteria: str) -> Experiment:
        exp = self.db.create_experiment(goal, success_criteria, self.budget.policy)
        self._current_experiment = exp
        return exp

    async def run_iteration(self, agent_type: str, task: str) -> Dict[str, Any]:
        """Run a single iteration with specified agent type."""
        if not self.budget.can_spend(100):  # Min budget check
            if self._current_experiment:
                self._current_experiment.status = "paused"
                self.db.update_experiment_status(self._current_experiment.id, "paused")
            return {"error": "Budget exhausted"}

        async with self.pacer:
            agent = self._get_agent(agent_type)
            if agent is None:
                return {"error": "No agent available"}

            # Run with appropriate backend
            try:
                if self._use_litellm:
                    result = await agent.run(task)
                    output = result.get("final_output", "")
                    tokens_used = result.get("usage", {}).get("total_tokens", 0)
                else:
                    result = await Runner.run(agent, task)
                    output = result.final_output
                    tokens_used = 0  # Would need to extract from response

                # Track token usage
                self.budget.track_tokens(tokens_used)

                iteration = self.db.add_iteration(
                    experiment_id=self._current_experiment.id,
                    agent_type=agent_type,
                    task=task,
                    result=output,
                    tokens_used=tokens_used
                )

                self.events.publish("iteration_complete", {
                    "experiment_id": self._current_experiment.id,
                    "iteration_id": iteration.id,
                    "agent_type": agent_type
                })

                return {"iteration": iteration, "result": output}
            except Exception as e:
                return {"error": str(e)}

    def _get_agent(self, agent_type: str) -> Optional[Any]:
        return self._agents.get(agent_type)

    def _on_iteration_complete(self, event: dict):
        # Update coordinator state
        pass

    def get_status(self) -> Dict[str, Any]:
        if not self._current_experiment:
            return {"status": "no_experiment"}
        return {
            "status": self._current_experiment.status,
            "tokens_used": self.budget.tokens_used,
            "budget": self.budget.policy.max_tokens_per_window,
            "backend": "litellm" if self._use_litellm else "agents-sdk"
        }
