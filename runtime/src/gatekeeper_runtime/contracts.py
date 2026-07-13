from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RunStep(str, Enum):
    INTAKE = "INTAKE"
    CLARIFY = "CLARIFY"
    PLAN = "PLAN"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    BUILD = "BUILD"
    REVIEW_RESULT = "REVIEW_RESULT"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


class PipelineStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NOT_RUN = "not_run"


class DoraOutput(BaseModel):
    status: Literal["PLAN_READY"]
    plan_file: str
    plan_markdown: str
    summary: str
    requirements: list[str] = Field(default_factory=list)
    files_to_modify: list[str] = Field(default_factory=list)
    complexity: Literal["XS", "S", "M", "L", "XL"]
    needs_human_approval: Literal[True]
    questions_remaining: list[str] = Field(default_factory=list)


class FileWrite(BaseModel):
    path: str
    content: str


class BobPipelineResult(BaseModel):
    tests: PipelineStatus
    review: PipelineStatus
    seo: PipelineStatus
    accessibility: PipelineStatus
    security: PipelineStatus
    cleanup: PipelineStatus
    ai_context: PipelineStatus
    documentation: PipelineStatus


class BobOutput(BaseModel):
    status: Literal["BUILD_DONE", "BUILD_BLOCKED"]
    ready_to_ship: Literal["yes", "no"]
    implementation_summary: str
    modified_files: list[str] = Field(default_factory=list)
    file_writes: list[FileWrite] = Field(default_factory=list)
    pipeline: BobPipelineResult
    blocking_reason: str = ""
    non_blocking_findings: list[str] = Field(default_factory=list)
