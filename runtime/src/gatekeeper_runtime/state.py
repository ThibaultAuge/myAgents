from __future__ import annotations

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .contracts import RunStep


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class RunState(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run-{uuid4().hex[:10]}")
    user_request: str
    current_step: RunStep = RunStep.INTAKE
    approved: bool = False
    plan_file: str = ""
    plan_summary: str = ""
    build_summary: str = ""
    blocked_reason: str = ""
    pending_question: str = ""
    modified_files: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

    def touch(self) -> None:
        self.updated_at = now_iso()
