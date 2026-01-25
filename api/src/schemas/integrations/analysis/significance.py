from enum import Enum

from pydantic import BaseModel


class SignificanceLevel(str, Enum):
    FEATURE = "FEATURE"  # High impact changes
    REFACTOR = "REFACTOR"  # Medium impact logic changes
    CHORE = "CHORE"  # Low impact/maintenance
    NOISE = "NOISE"  # Ignored/Zero impact


class FileChange(BaseModel):
    filename: str
    additions: int
    deletions: int


class SignificanceResult(BaseModel):
    score: float
    classification: SignificanceLevel
    is_significant: bool
