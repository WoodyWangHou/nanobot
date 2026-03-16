# CLI commands for swarm
import typer
from pathlib import Path
from ..swarm.coordinator import SwarmCoordinator
from ..swarm.storage.database import Database
from ..swarm.storage.models import BudgetPolicy
from ..channel_adapter import ChannelAdapter

app = typer.Typer(help="Swarm commands")


def _parse_budget(budget: str) -> tuple[int, str]:
    """Parse budget string like '10k/1h' -> (10000, '1h')"""
    parts = budget.lower().split("/")
    if len(parts) != 2:
        raise ValueError("Budget must be in format: '10k/1h'")

    # Parse token count
    token_str = parts[0]
    if token_str.endswith("k"):
        tokens = int(token_str[:-1]) * 1000
    elif token_str.endswith("m"):
        tokens = int(token_str[:-1]) * 1000000
    else:
        tokens = int(token_str)

    # Parse duration
    duration = parts[1]

    return tokens, duration


@app.command()
def start(
    goal: str = typer.Argument(..., help="Experiment goal"),
    budget: str = typer.Option("10k/1h", help="Budget in format '10k/1h'"),
    model: str = typer.Option("gpt-4o", help="Model to use"),
    db_path: str = typer.Option("swarm.db", help="Database path"),
):
    """Start a new experiment."""
    tokens, window = _parse_budget(budget)
    policy = BudgetPolicy(max_tokens_per_window=tokens, window_duration=window)
    db = Database(db_path)
    coordinator = SwarmCoordinator(db, policy, model=model)

    import asyncio
    exp = asyncio.run(coordinator.start_experiment(goal, ""))
    typer.echo(f"Experiment started: {exp.id}")
    typer.echo(f"Model: {model}")
    typer.echo(f"Budget: {tokens} tokens per {window}")


@app.command()
def status(
    db_path: str = typer.Option("swarm.db", help="Database path"),
):
    """Check experiment status."""
    db = Database(db_path)
    # This would need a coordinator instance - simplified for now
    typer.echo("Use /status command in chat interface")


@app.command()
def progress(
    experiment_id: str = typer.Argument(..., help="Experiment ID"),
    db_path: str = typer.Option("swarm.db", help="Database path"),
):
    """Get experiment progress."""
    from ..swarm.tracker.progress import ProgressTracker
    db = Database(db_path)
    tracker = ProgressTracker(db)
    summary = tracker.summarize(experiment_id)
    typer.echo(summary)


if __name__ == "__main__":
    app()
