"""The Naked Barbie: the minimal reusable agent model."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
@dataclass
class AgentRun:
    run_id: int; target: str; status: str; report_path: str
class BaseBarbie:
    name="Naked Barbie"; theme="base"; description="A neutral, auditable shell for specialized agents."
    def now(self)->str: return datetime.now(timezone.utc).isoformat()
    def manifest(self)->dict[str,Any]: return {"name":self.name,"theme":self.theme,"description":self.description,"capabilities":[],"created_at":self.now()}
