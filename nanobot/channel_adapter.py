# Channel adapter to integrate swarm with nanobot channels
"""
Adapter to integrate swarm with nanobot channels.
Preserves existing channel implementations while routing swarm messages.
"""
from typing import Optional
from .swarm.coordinator import SwarmCoordinator
from .swarm.storage.database import Database
from .swarm.storage.models import BudgetPolicy
from .swarm.tracker.progress import ProgressTracker


class ChannelAdapter:
    """Routes messages between nanobot channels and swarm coordinator."""

    def __init__(self, coordinator: Optional[SwarmCoordinator] = None, db: Optional[Database] = None):
        self.coordinator = coordinator
        self.db = db
        self.tracker = ProgressTracker(db) if db else None

    async def handle_message(self, message: str, user_id: str) -> str:
        """Handle incoming message and return response."""
        if not self.coordinator:
            return "Swarm not initialized"

        # Parse commands
        if message.startswith("/experiment"):
            return await self._handle_command(message)

        if message.startswith("/status"):
            return await self._handle_status(message)

        if message.startswith("/progress"):
            return await self._handle_progress(message)

        # Forward to coordinator
        return await self._forward_to_swarm(message)

    async def _handle_command(self, command: str) -> str:
        parts = command.split()
        if len(parts) < 2:
            return "Usage: /experiment <start|pause|resume|cancel|status>"

        cmd = parts[1]
        if cmd == "start":
            goal = " ".join(parts[2:]) if len(parts) > 2 else ""
            exp = await self.coordinator.start_experiment(goal, "")
            return f"Experiment started: {exp.id}"
        elif cmd == "status":
            status = self.coordinator.get_status()
            return f"Status: {status}"
        elif cmd == "pause":
            if self.coordinator._current_experiment:
                self.coordinator._current_experiment.status = "paused"
                self.db.update_experiment_status(self.coordinator._current_experiment.id, "paused")
                return "Experiment paused"
            return "No active experiment"
        elif cmd == "resume":
            if self.coordinator._current_experiment:
                self.coordinator._current_experiment.status = "running"
                self.db.update_experiment_status(self.coordinator._current_experiment.id, "running")
                return "Experiment resumed"
            return "No paused experiment"

        return f"Unknown command: {cmd}"

    async def _handle_status(self, command: str) -> str:
        if not self.coordinator:
            return "Swarm not initialized"
        status = self.coordinator.get_status()
        return f"Swarm Status: {status}"

    async def _handle_progress(self, command: str) -> str:
        if not self.tracker or not self.coordinator._current_experiment:
            return "No active experiment"
        return self.tracker.summarize(self.coordinator._current_experiment.id)

    async def _forward_to_swarm(self, message: str) -> str:
        if not self.coordinator._current_experiment:
            return "No active experiment. Use /experiment start <goal> to begin."
        return "Processing request through swarm..."
