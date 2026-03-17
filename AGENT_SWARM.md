# Agent Swarm Setup Guide

This guide explains how to set up and configure the Agent Swarm mode in nanobot.

## Overview

Agent Swarm is a self-improving multi-agent framework that orchestrates specialized agents (Researcher, Executor, Reviewer) to accomplish complex tasks with budget control and progress tracking.

## Requirements

### Python Dependencies

```bash
pip install nanobot-ai[dev]
```

Required packages (already in nanobot):
- `openai-agents` - For OpenAI Agents SDK
- `litellm` - For multi-provider support (MiniMax, Gemini, etc.)
- `aiosqlite` - For SQLite storage

### API Keys

Depending on which model you want to use, set the appropriate environment variables:

| Provider | Environment Variable | Example |
|----------|---------------------|---------|
| OpenAI | `OPENAI_API_KEY` | `sk-...` |
| MiniMax | `MINIMAX_API_KEY` | Get from console.minimax.io |
| Gemini | `GEMINI_API_KEY` | Get from aistudio.google.com |
| Anthropic | `ANTHROPIC_API_KEY` | Get from console.anthropic.com |
| DeepSeek | `DEEPSEEK_API_KEY` | Get from platform.deepseek.com |

## Configuration

### 1. Create Workspace Directory

```bash
mkdir -p ~/.nanobot/workspace
```

### 2. Configure Models (config.json)

Edit `~/.nanobot/config.json` to add your providers:

```json
{
  "providers": {
    "openai": {
      "api_key": "your-openai-key"
    },
    "minimax": {
      "api_key": "your-minimax-key"
    },
    "gemini": {
      "api_key": "your-gemini-key"
    }
  },
  "model": "gpt-4o",
  "channels": {}
}
```

### 3. Environment Variables

For better security, use environment variables instead of hardcoding keys:

```bash
# Option 1: Set in shell
export OPENAI_API_KEY="sk-..."
export MINIMAX_API_KEY="your-minimax-key"
export GEMINI_API_KEY="your-gemini-key"

# Option 2: Use .env file
# Create ~/.nanobot/.env
OPENAI_API_KEY=sk-...
MINIMAX_API_KEY=your-minimax-key
GEMINI_API_KEY=your-gemini-key
```

## Usage

### CLI Commands

#### Start an Experiment

```bash
# Using OpenAI model
nanobot swarm start "Research the latest developments in quantum computing" --budget 100k/1h --model gpt-4o

# Using MiniMax model
nanobot swarm start "Analyze market trends" --budget 50k/1h --model minimax/MiniMax-M2.1

# Using Gemini model
nanobot swarm start "Write a summary of AI news" --budget 30k/1h --model gemini/gemini-2.0-flash
```

Budget format: `<tokens>/<duration>`
- Tokens: `10k` (10,000), `100k` (100,000), `1m` (1,000,000)
- Duration: `1h` (1 hour), `24h` (24 hours), `7d` (7 days)

#### Check Progress

```bash
nanobot swarm progress <experiment-id>
```

### Programmatic Usage

```python
import asyncio
from nanobot.swarm.coordinator import SwarmCoordinator
from nanobot.swarm.storage.database import Database
from nanobot.swarm.storage.models import BudgetPolicy

async def main():
    # Create database and policy
    db = Database("swarm.db")
    policy = BudgetPolicy(
        max_tokens_per_window=100000,
        window_duration="1h",
        auto_pause=True,
        warning_at_percent=80
    )

    # Create coordinator with your model
    # Use LiteLLM model names for non-OpenAI providers
    coordinator = SwarmCoordinator(
        db, policy,
        model="minimax/MiniMax-M2.1"  # or "gemini/gemini-pro", "gpt-4o", etc.
    )

    # Start experiment
    exp = await coordinator.start_experiment(
        goal="Research AI trends in 2026",
        success_criteria="Comprehensive report with sources"
    )
    print(f"Experiment started: {exp.id}")

    # Run iterations with different agent types
    result = await coordinator.run_iteration(
        agent_type="researcher",
        task="Find latest developments in AI agents"
    )
    print(f"Result: {result}")

    # Check progress
    status = coordinator.get_status()
    print(f"Status: {status}")

    # Get detailed progress
    from nanobot.swarm.tracker.progress import ProgressTracker
    tracker = ProgressTracker(db)
    summary = tracker.summarize(exp.id)
    print(summary)

asyncio.run(main())
```

### Channel Integration

You can also interact with the swarm through nanobot channels (Telegram, Discord, etc.):

```python
from nanobot.channel_adapter import ChannelAdapter
from nanobot.swarm.coordinator import SwarmCoordinator
from nanobot.swarm.storage.database import Database
from nanobot.swarm.storage.models import BudgetPolicy

# Initialize
db = Database("swarm.db")
policy = BudgetPolicy(max_tokens_per_window=100000, window_duration="1h")
coordinator = SwarmCoordinator(db, policy, model="gpt-4o")
adapter = ChannelAdapter(coordinator, db)

# Handle messages
async def handle_user_message(message: str, user_id: str):
    response = await adapter.handle_message(message, user_id)
    return response
```

Available commands in chat:
- `/experiment start <goal>` - Start new experiment
- `/experiment status` - Check experiment status
- `/experiment pause` - Pause experiment
- `/experiment resume` - Resume experiment
- `/progress` - Show progress

## Supported Models

| Model | Provider | Model String | Notes |
|-------|----------|--------------|-------|
| GPT-4o | OpenAI | `gpt-4o` | Uses OpenAI Agents SDK |
| GPT-4o Mini | OpenAI | `gpt-4o-mini` | Faster, cheaper |
| MiniMax | MiniMax | `minimax/MiniMax-M2.1` | LiteLLM |
| Gemini | Google | `gemini/gemini-pro` | LiteLLM |
| Gemini Flash | Google | `gemini/gemini-2.0-flash` | LiteLLM |
| Claude | Anthropic | `claude-3-opus-20240229` | LiteLLM |
| DeepSeek | DeepSeek | `deepseek-chat` | LiteLLM |
| Qwen | DashScope | `qwen-max` | LiteLLM |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SwarmCoordinator                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Researcher │  │  Executor   │  │  Reviewer   │        │
│  │   Agent     │  │   Agent     │  │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    BudgetController                         │
│  - Token tracking    - Rate limiting    - Auto-pause      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      SQLite Storage                         │
│  - Experiments    - Iterations    - Learnings             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      EventBus                               │
│  - Progress updates  - External notifications              │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### "No module named 'agents'"

Install OpenAI Agents SDK:
```bash
pip install openai-agents
```

### "API key not found"

Make sure your API key is set:
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Or set it
export OPENAI_API_KEY="your-key"
```

### "Budget exhausted"

The experiment has hit its budget limit. You can:
1. Start a new experiment with higher budget
2. Wait for the budget window to reset (e.g., 1 hour)

### "Model not supported"

If using LiteLLM models, ensure the provider is configured in `config.json`:
```json
{
  "providers": {
    "minimax": {
      "api_key": "your-key"
    }
  }
}
```

## Examples

### Research Task

```python
# Start research experiment
coordinator = SwarmCoordinator(db, policy, model="minimax/MiniMax-M2.1")
exp = await coordinator.start_experiment(
    goal="Research quantum computing advances",
    success_criteria="5 key findings with sources"
)

# Run research
result = await coordinator.run_iteration("researcher", "What are the latest breakthroughs in quantum computing?")
```

### Multi-Agent Workflow

```python
# Research phase
result1 = await coordinator.run_iteration("researcher", "Research the topic")

# Execution phase
result2 = await coordinator.run_iteration("executor", "Implement the solution based on research")

# Review phase
result3 = await coordinator.run_iteration("reviewer", "Review the implementation and suggest improvements")
```
