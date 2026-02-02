from abc import ABC, abstractmethod

from src.schemas.integrations.ai.timeline_analysis import AnalysisResult


class AIProvider(ABC):
    @abstractmethod
    async def analyze_payload(self, prompt_context: str) -> AnalysisResult:
        """Just take the string and give back the result."""
        pass
