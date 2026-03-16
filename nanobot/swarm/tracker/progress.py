# Progress tracker for experiments
from typing import Dict, Any, List
from ..storage.database import Database


class ProgressTracker:
    def __init__(self, db: Database):
        self.db = db

    def get_progress(self, experiment_id: str) -> Dict[str, Any]:
        """Get progress metrics for an experiment."""
        experiment = self.db.get_experiment(experiment_id)
        if not experiment:
            return {"error": "Experiment not found"}

        iterations = self.db.get_iterations(experiment_id)

        # Calculate learnings from all iterations
        all_learnings: List[str] = []
        for iteration in iterations:
            all_learnings.extend(iteration.learnings)

        # Calculate progress percent (based on iterations completed)
        # For now, just return iteration count as progress
        return {
            "experiment_id": experiment_id,
            "iterations": len(iterations),
            "status": experiment.status,
            "tokens_used": experiment.tokens_used,
            "budget": experiment.budget_policy.max_tokens_per_window,
            "percent": min(100, len(iterations) * 10),  # Simple heuristic
            "learnings": all_learnings
        }

    def summarize(self, experiment_id: str) -> str:
        """Get a text summary of experiment progress."""
        progress = self.get_progress(experiment_id)
        if "error" in progress:
            return f"Error: {progress['error']}"

        return f"""Experiment Progress:
- Status: {progress['status']}
- Iterations: {progress['iterations']}
- Tokens Used: {progress['tokens_used']}/{progress['budget']}
- Progress: {progress['percent']}%
- Learnings: {len(progress['learnings'])}"""
