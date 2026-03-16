# Budget controller with rate limiting
from datetime import datetime, timedelta
from dataclasses import dataclass
import re


@dataclass
class BudgetPolicy:
    max_tokens_per_window: int
    window_duration: str  # "1h", "24h"
    auto_pause: bool = True
    warning_at_percent: int = 80


class BudgetController:
    def __init__(self, policy: BudgetPolicy):
        self.policy = policy
        self.tokens_used = 0
        self.window_start = datetime.utcnow()

    def can_spend(self, amount: int) -> bool:
        self._check_window_reset()
        return (self.tokens_used + amount) <= self.policy.max_tokens_per_window

    def track_tokens(self, amount: int):
        self._check_window_reset()
        self.tokens_used += amount

    def should_warn(self) -> bool:
        if self.policy.max_tokens_per_window == 0:
            return False
        return (self.tokens_used / self.policy.max_tokens_per_window * 100) >= self.policy.warning_at_percent

    def should_pause(self) -> bool:
        if self.policy.max_tokens_per_window == 0:
            return False
        return self.tokens_used >= self.policy.max_tokens_per_window

    def _check_window_reset(self):
        duration = self._parse_duration(self.policy.window_duration)
        if datetime.utcnow() - self.window_start > duration:
            self.tokens_used = 0
            self.window_start = datetime.utcnow()

    def _parse_duration(self, duration: str) -> timedelta:
        match = re.match(r"(\d+)h", duration)
        if match:
            return timedelta(hours=int(match.group(1)))
        match = re.match(r"(\d+)m", duration)
        if match:
            return timedelta(minutes=int(match.group(1)))
        match = re.match(r"(\d+)s", duration)
        if match:
            return timedelta(seconds=int(match.group(1)))
        match = re.match(r"(\d+)d", duration)
        if match:
            return timedelta(days=int(match.group(1)))
        return timedelta(hours=1)
