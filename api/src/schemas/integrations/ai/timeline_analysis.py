from enum import Enum

from pydantic import BaseModel

from src.schemas.timelines import TimelineNodeBase


class AnalysisAction(str, Enum):
    CREATE_NODE = "CREATE_NODE"
    MERGE_TO_PARENT = "MERGE_TO_PARENT"
    IGNORE = "IGNORE"


class AnalysisResult(BaseModel):
    action: AnalysisAction
    node_content: TimelineNodeBase | None = None
    tech_stack: list[str] = []
    reasoning: str
