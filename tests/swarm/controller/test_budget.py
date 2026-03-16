# Test budget controller
import pytest
from nanobot.swarm.controller.budget import BudgetController, BudgetPolicy


def test_budget_enforcement():
    policy = BudgetPolicy(
        max_tokens_per_window=10000,
        window_duration="1h",
        auto_pause=True,
        warning_at_percent=80
    )
    controller = BudgetController(policy)

    # Should allow
    assert controller.can_spend(5000) == True

    # Should warn at 80%
    controller.track_tokens(8000)
    assert controller.should_warn() == True

    # Should block at limit (when trying to spend more than available)
    assert controller.can_spend(3000) == False

    # At exactly at limit, should_pause should be True
    controller.track_tokens(2000)  # Now at 10000
    assert controller.should_pause() == True


def test_budget_window_reset():
    import time
    policy = BudgetPolicy(
        max_tokens_per_window=1000,
        window_duration="1s",  # 1 second for testing
        auto_pause=True,
        warning_at_percent=80
    )
    controller = BudgetController(policy)

    # At 500 tokens, trying to spend 600 should fail (500+600=1100 > 1000)
    controller.track_tokens(500)
    assert controller.can_spend(600) == False

    # Wait for window to reset
    time.sleep(1.5)
    # After reset, should be able to spend 600
    assert controller.can_spend(600) == True


def test_zero_budget():
    policy = BudgetPolicy(
        max_tokens_per_window=0,
        window_duration="1h",
        auto_pause=True,
        warning_at_percent=80
    )
    controller = BudgetController(policy)

    # Zero budget should not warn or pause
    assert controller.should_warn() == False
    assert controller.should_pause() == False
