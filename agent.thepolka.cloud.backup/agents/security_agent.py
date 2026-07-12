from __future__ import annotations
from urllib.parse import urlparse
from agents.base_agent import AgentRun,BaseBarbie
from config.settings import ALLOWED_TARGETS
from database.store import Store
from reports.html import write
from scanners.base import Finding
from scanners.headers_scan import HeadersScanner
from scanners.ssl_scan import TLSScanner
from scanners.dns_scan import DNSScanner
from scanners.discovery_scan import DiscoveryScanner
class SecurityBarbie(BaseBarbie):
 name="Security Barbie";theme="security";description="Safe daily posture checks and reports.";scanners=(HeadersScanner(),TLSScanner(),DNSScanner(),DiscoveryScanner())
 def _target(self,target):
  if not target.startswith(("http://","https://")):target="https://"+target
  host=(urlparse(target).hostname or "").lower()
  if host not in ALLOWED_TARGETS:raise PermissionError(f"{host!r} is outside ALLOWED_TARGETS. Add it to .env only if you own or are authorized to scan it.")
  return target.rstrip("/")
 def run(self,target):
  target=self._target(target);store=Store();run_id=store.begin(self.name,target,self.now());findings=[];status="complete"
  for scanner in self.scanners:
   try:findings.extend(f.to_dict() for f in scanner.scan(target))
   except Exception as exc:findings.append(Finding(scanner.name,"info",f"Check unavailable: {scanner.name}",str(exc),"Confirm connectivity and retry.").to_dict());status="completed_with_errors"
  provisional=store.get(run_id);provisional["findings"]=findings;provisional["status"]=status;path=write(provisional);store.finish(run_id,self.now(),status,findings,path);return AgentRun(run_id,target,status,path)
 def run_daily(self):return [self.run(host) for host in sorted(ALLOWED_TARGETS)]
 def regenerate_report(self,run_id):return write(Store().get(run_id))
