from __future__ import annotations
import urllib.request
from urllib.parse import urljoin
from .base import Finding,SafeScanner
from config.settings import TIMEOUT,USER_AGENT
class DiscoveryScanner(SafeScanner):
 name="discovery"
 def scan(self,target):
  findings=[]
  for path,title,advice in [("/.well-known/security.txt","security.txt","Publish a security.txt with a monitored contact."),("/robots.txt","robots.txt","Review robots directives; they are not access control.")]:
   try:
    req=urllib.request.Request(urljoin(target,path),headers={"User-Agent":USER_AGENT},method="GET")
    with urllib.request.urlopen(req,timeout=TIMEOUT) as r:status=r.status
    findings.append(Finding(self.name,"info",f"{title} available",f"HTTP {status}",advice))
   except Exception:
    if title=="security.txt":findings.append(Finding(self.name,"low","security.txt not found","No successful response at /.well-known/security.txt",advice))
  return findings
