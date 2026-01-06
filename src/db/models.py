from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class ScanSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    source: str = Field(description="image|text")
    raw_text: str
    cleaned_text: str
    safety_label: str
    contains_count: int
    may_contain_count: int
    total_detected: int
    duration_ms: Optional[float] = None
    user_label: Optional[str] = Field(default=None, description="Optional user identifier")


class AllergenFinding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="scansession.id", index=True)
    allergen: str
    category: str  # CONTAINS or MAY_CONTAIN
    confidence: float
    evidence: str
    cleaned_trigger_phrase: Optional[str] = None
    keyword: Optional[str] = None
    severity: Optional[str] = None
    symptoms: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    immediate_actions: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    when_to_seek_help: Optional[str] = None
    alternatives: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    summary: Optional[str] = None
