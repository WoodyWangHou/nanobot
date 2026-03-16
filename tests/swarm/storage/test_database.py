# Test database storage
import pytest
from nanobot.swarm.storage.database import Database
from nanobot.swarm.storage.models import BudgetPolicy


def test_create_experiment():
    db = Database(":memory:")
    policy = BudgetPolicy(
        max_tokens_per_window=10000,
        window_duration="1h",
        auto_pause=True,
        warning_at_percent=80
    )
    exp = db.create_experiment(
        goal="test goal",
        success_criteria="test criteria",
        budget_policy=policy
    )
    assert exp.id is not None
    assert exp.goal == "test goal"
    assert exp.status == "running"


def test_add_iteration():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment("test goal", "criteria", policy)

    iteration = db.add_iteration(
        experiment_id=exp.id,
        agent_type="researcher",
        task="research task",
        result="research result",
        learnings=["learned something"],
        feedback="good work"
    )

    assert iteration.id is not None
    assert iteration.experiment_id == exp.id
    assert iteration.agent_type == "researcher"


def test_get_iterations():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment("test goal", "criteria", policy)

    db.add_iteration(exp.id, "researcher", "task1", "result1")
    db.add_iteration(exp.id, "executor", "task2", "result2")

    iterations = db.get_iterations(exp.id)
    assert len(iterations) == 2


def test_update_experiment_status():
    db = Database(":memory:")
    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment("test goal", "criteria", policy)

    db.update_experiment_status(exp.id, "paused")

    updated = db.get_experiment(exp.id)
    assert updated.status == "paused"
