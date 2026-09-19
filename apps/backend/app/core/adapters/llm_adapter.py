"""
Adapter layer forwarding LLM requests to app.core.llm.get_llm_provider().
Ensures single source of truth for LLM provider selection and configuration.
"""

from typing import Dict, Any, Optional
from app.core.llm import get_llm_provider, LLMProvider


class LLMAdapter:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        return self._provider or get_llm_provider()

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        return await self.provider.generate_json(prompt, system_prompt or "")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return await self.provider.generate_text(prompt, system_prompt or "")


llm_adapter = LLMAdapter()
