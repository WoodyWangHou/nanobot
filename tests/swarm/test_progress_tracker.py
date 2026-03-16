# Test progress tracker
import pytest
from nanobot.swarm.tracker.progress import ProgressTracker
from nanobot.swarm.storage.database import Database
from nanobot.swarm.storage.models import BudgetPolicy


def test_progress_calculation():
    db = Database(":memory:")
    tracker = ProgressTracker(db)

    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment(
        goal="test",
        success_criteria="success",
        budget_policy=policy
    )

    progress = tracker.get_progress(exp.id)
    assert progress["percent"] == 0
    assert progress["iterations"] == 0


def test_progress_with_iterations():
    db = Database(":memory:")
    tracker = ProgressTracker(db)

    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment("test", "success", policy)

    # Add some iterations
    db.add_iteration(exp.id, "researcher", "task1", "result1", learnings=["learned1"])
    db.add_iteration(exp.id, "executor", "task2", "result2", learnings=["learned2"])

    progress = tracker.get_progress(exp.id)
    assert progress["iterations"] == 2
    assert len(progress["learnings"]) == 2


def test_progress_summarize():
    db = Database(":memory:")
    tracker = ProgressTracker(db)

    policy = BudgetPolicy(max_tokens_per_window=10000, window_duration="1h")
    exp = db.create_experiment("test goal", "success criteria", policy)

    summary = tracker.summarize(exp.id)
    assert "test goal" in summary or "Status" in summary
