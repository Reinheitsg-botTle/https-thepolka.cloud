from __future__ import annotations
import urllib.request
from .base import Finding,SafeScanner
from config.settings import TIMEOUT,USER_AGENT
class HeadersScanner(SafeScanner):
 name="headers"
 required={"strict-transport-security":("medium","Add HSTS after confirming every subdomain supports HTTPS."),"content-security-policy":("medium","Define a restrictive Content-Security-Policy."),"x-content-type-options":("low","Set X-Content-Type-Options: nosniff."),"referrer-policy":("low","Set a privacy-preserving Referrer-Policy."),"permissions-policy":("low","Explicitly limit browser permissions with Permissions-Policy.")}
 def scan(self,target):
  req=urllib.request.Request(target,headers={"User-Agent":USER_AGENT},method="GET")
  with urllib.request.urlopen(req,timeout=TIMEOUT) as response:
   headers={k.lower():v for k,v in response.headers.items()};findings=[]
   for key,(severity,advice) in self.required.items():
    if not headers.get(key): findings.append(Finding(self.name,severity,f"Missing {key}","Response did not include this header.",advice))
   if headers.get("server"):findings.append(Finding(self.name,"info","Server header exposed",f"Server: {headers['server']}","Consider minimizing version/banner disclosure."))
   return findings
