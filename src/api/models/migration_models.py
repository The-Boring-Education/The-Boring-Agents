"""Pydantic models for content migration endpoints."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    DSA_QUESTIONS = "dsa-questions"
    INTERVIEW_SHEETS = "interview-sheets"
    APTITUDE = "aptitude"
    QUIZZES = "quizzes"
    ALL = "all"


class MigrateRequest(BaseModel):
    content_types: List[ContentType] = Field(
        default=[ContentType.ALL],
        description="Which content types to migrate",
    )
    dry_run: bool = Field(
        default=True,
        description="If true, shows what would change without making changes",
    )
    source_env: str = Field(
        default="dev",
        description="Source environment to export from (dev | prod | local)",
    )
    target_env: str = Field(
        default="prod",
        description="Target environment to sync to (dev | prod | local)",
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters: topics, slugs, domain, difficulty, categoryNames",
    )
    source_admin_secret: Optional[str] = None
    target_admin_secret: Optional[str] = None


class MigrationStatus(BaseModel):
    ok: bool
    message: str
    dry_run: bool = False
    source: str = ""
    target: str = ""
    results: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class ExportRequest(BaseModel):
    env: str = Field(default="dev", description="Environment to export from")
    content_types: List[ContentType] = Field(default=[ContentType.ALL])
    filters: Optional[Dict[str, Any]] = None
    admin_secret: Optional[str] = None
    save_to_file: bool = Field(default=True)


class SyncRequest(BaseModel):
    env: str = Field(default="prod", description="Environment to sync to")
    content_type: ContentType
    data: Dict[str, Any] = Field(description="Content data to sync")
    dry_run: bool = True
    admin_secret: Optional[str] = None
