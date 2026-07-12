from __future__ import annotations
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load_dotenv():
 p=ROOT/".env"
 if p.exists():
  for line in p.read_text().splitlines():
   if "=" in line and not line.lstrip().startswith("#"):
    k,v=line.split("=",1); os.environ.setdefault(k.strip(),v.strip())
load_dotenv()
ALLOWED_TARGETS={x.strip().lower() for x in os.getenv("ALLOWED_TARGETS","agent.thepolka.cloud").split(",") if x.strip()}
TIMEOUT=int(os.getenv("SCAN_TIMEOUT_SECONDS","12")); USER_AGENT=os.getenv("SCAN_USER_AGENT","PolkaSecurityBarbie/1.0"); PORT=int(os.getenv("PORT","8080"))
HOURLY_RATE_USD=float(os.getenv("HOURLY_RATE_USD","125")); MINUTES_SAVED_PER_SCAN=float(os.getenv("MINUTES_SAVED_PER_SCAN","45"))
DATA_DIR=ROOT/"data"; REPORT_DIR=ROOT/"reports"/"output"
for folder in (DATA_DIR,REPORT_DIR,ROOT/"logs"): folder.mkdir(parents=True,exist_ok=True)
