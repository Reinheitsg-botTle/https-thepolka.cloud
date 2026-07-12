from __future__ import annotations
from dataclasses import dataclass,asdict
@dataclass
class Finding:
 scanner:str;severity:str;title:str;evidence:str;recommendation:str
 def to_dict(self):return asdict(self)
class SafeScanner:
 name="base"
 def scan(self,target):raise NotImplementedError
