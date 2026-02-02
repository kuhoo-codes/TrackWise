from openai import AsyncOpenAI

from src.core.config import settings
from src.exceptions.ai import AIServiceError
from src.schemas.integrations.ai.timeline_analysis import AnalysisResult
from src.services.integrations.ai.base_provider import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self, model: str = "llama3.2") -> None:
        self.client = AsyncOpenAI(base_url=settings.OLLAMA_URL + "/v1", api_key="ollama")
        self.model = model

    async def analyze_payload(self, prompt_context: str) -> AnalysisResult:
        """
        Uses local Ollama to analyze the cluster with a professional CTO persona.
        """
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Senior Technical Recruiter and CTO. Your goal is to transform "
                            "messy developer git logs into high-impact professional achievements. "
                            "Use strong action verbs (Architected, Spearheaded, Optimized). "
                            "Focus on the 'Why' and 'Impact', not just the 'What'."
                        ),
                    },
                    {"role": "user", "content": prompt_context},
                ],
                response_format=AnalysisResult,
                temperature=0.0,
            )

            return response.choices[0].message.parsed

        except Exception as e:
            raise AIServiceError(message="Ollama AI service error", details={"error": str(e)}) from e
