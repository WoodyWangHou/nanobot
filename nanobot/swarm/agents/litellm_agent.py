# LiteLLM-based agent fallback for models not supported by OpenAI Agents SDK
# Supports MiniMax, Gemini, and any other LiteLLM-compatible models
from typing import Optional, Dict, Any, List
import litellm


class LiteLLMAgent:
    """A LiteLLM-based agent that works with any supported model."""

    def __init__(self, name: str, instructions: str, model: str = "gpt-4o"):
        self.name = name
        self.instructions = instructions
        self.model = model

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute a task using LiteLLM."""
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": task}
        ]

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            return {
                "final_output": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "final_output": f"Error: {str(e)}",
                "usage": {"total_tokens": 0}
            }


def create_litellm_agent(name: str, instructions: str, model: str) -> LiteLLMAgent:
    """Factory function to create a LiteLLM-based agent."""
    return LiteLLMAgent(name=name, instructions=instructions, model=model)
