import logging
from typing import Optional
from app.ai.base import BaseAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIFactory:
    @staticmethod
    def get_provider(preferred: Optional[str] = None) -> BaseAIProvider:
        """
        Dynamically selects the AI provider based on preference and active key availability.
        Fallback order: Preferred -> Alternative Provider -> Base with informative errors.
        """
        choice = (preferred or settings.PREFERRED_AI_PROVIDER).lower()

        if choice == "openai":
            if settings.OPENAI_API_KEY:
                return OpenAIProvider()
            if settings.GEMINI_API_KEY:
                logger.info("OpenAI API key missing, falling back to Google Gemini.")
                return GeminiProvider()
            return OpenAIProvider()
        else:
            if settings.GEMINI_API_KEY:
                return GeminiProvider()
            if settings.OPENAI_API_KEY:
                logger.info("Gemini API key missing, falling back to OpenAI.")
                return OpenAIProvider()
            return GeminiProvider()
