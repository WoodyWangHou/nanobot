# Storage models for swarm experiments
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BudgetPolicy(BaseModel):
    max_tokens_per_window: int
    window_duration: str  # "1h", "24h"
    auto_pause: bool = True
    warning_at_percent: int = 80


class Experiment(BaseModel):
    id: str
    goal: str
    success_criteria: str
    status: str  # running, paused, completed, cancelled
    budget_policy: BudgetPolicy
    tokens_used: int = 0
    created_at: datetime
    updated_at: datetime


class Iteration(BaseModel):
    id: int
    experiment_id: str
    agent_type: str  # researcher, executor, reviewer
    task: str
    result: str
    learnings: list[str] = []
    feedback: Optional[str] = None
    tokens_used: int = 0
    created_at: datetime
