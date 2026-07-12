from __future__ import annotations
import socket,ssl
from datetime import datetime,timezone
from urllib.parse import urlparse
from .base import Finding,SafeScanner
from config.settings import TIMEOUT
class TLSScanner(SafeScanner):
 name="tls"
 def scan(self,target):
  host=urlparse(target).hostname or target;context=ssl.create_default_context()
  with socket.create_connection((host,443),timeout=TIMEOUT) as raw:
   with context.wrap_socket(raw,server_hostname=host) as sock:cert=sock.getpeercert();cipher=sock.cipher()
  expiry=datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc);days=(expiry-datetime.now(timezone.utc)).days
  if days<0:return [Finding(self.name,"critical","TLS certificate expired",cert["notAfter"],"Renew the certificate immediately.")]
  if days<21:return [Finding(self.name,"high","TLS certificate expires soon",f"{days} days remaining","Renew and deploy the certificate before expiry.")]
  return [Finding(self.name,"info","TLS certificate valid",f"Expires in {days} days; cipher {cipher[0]}","Continue certificate monitoring.")]
