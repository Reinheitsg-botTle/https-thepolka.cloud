from __future__ import annotations
import json,sqlite3
from config.settings import DATA_DIR,HOURLY_RATE_USD,MINUTES_SAVED_PER_SCAN
class Store:
 def __init__(self):
  self.db=sqlite3.connect(DATA_DIR/"barbie.db");self.db.row_factory=sqlite3.Row
  self.db.execute("CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY,agent TEXT NOT NULL,target TEXT NOT NULL,started_at TEXT NOT NULL,completed_at TEXT,status TEXT NOT NULL,findings_json TEXT NOT NULL,report_path TEXT)");self.db.commit()
 def begin(self,agent,target,started_at):
  cur=self.db.execute("INSERT INTO runs(agent,target,started_at,status,findings_json) VALUES(?,?,?,?,?)",(agent,target,started_at,"running","[]"));self.db.commit();return int(cur.lastrowid)
 def finish(self,run_id,completed_at,status,findings,report_path):
  self.db.execute("UPDATE runs SET completed_at=?,status=?,findings_json=?,report_path=? WHERE id=?",(completed_at,status,json.dumps(findings),report_path,run_id));self.db.commit()
 def get(self,run_id):
  row=self.db.execute("SELECT * FROM runs WHERE id=?",(run_id,)).fetchone()
  if not row: raise KeyError(f"Run {run_id} does not exist")
  d=dict(row);d["findings"]=json.loads(d.pop("findings_json"));return d
 def recent(self,limit=20):
  rows=self.db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?",(limit,)).fetchall();return [{**dict(r),"findings":json.loads(r["findings_json"])} for r in rows]
 def metrics(self):
  count=self.db.execute("SELECT count(*) FROM runs WHERE status LIKE 'complete%' ").fetchone()[0]
  saved_hours=count*MINUTES_SAVED_PER_SCAN/60;return {"completed_scans":count,"estimated_hours_saved":round(saved_hours,1),"estimated_savings_usd":round(saved_hours*HOURLY_RATE_USD,2),"hourly_rate_usd":HOURLY_RATE_USD,"minutes_saved_per_scan":MINUTES_SAVED_PER_SCAN}
