from google import genai

from src.schemas.integrations.ai.timeline_analysis import AnalysisResult
from src.services.integrations.ai.base_provider import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-flash-latest") -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def analyze_payload(self, prompt_context: str) -> AnalysisResult:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt_context,
            config={
                "system_instruction": (
                    "You are a Senior Technical Recruiter and CTO. Your goal is to transform "
                    "messy developer git logs into high-impact professional achievements. "
                    "Use strong action verbs (Architected, Spearheaded, Optimized). "
                    "Focus on the 'Why' and 'Impact', not just the 'What'."
                ),
                "response_mime_type": "application/json",
                "response_schema": AnalysisResult,
            },
        )
        return response.parsed
