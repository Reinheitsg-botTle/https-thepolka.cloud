from __future__ import annotations
import socket
from urllib.parse import urlparse
from .base import Finding,SafeScanner
class DNSScanner(SafeScanner):
 name="dns"
 def scan(self,target):
  host=urlparse(target).hostname or target;addresses=sorted({item[4][0] for item in socket.getaddrinfo(host,None)});return [Finding(self.name,"info","DNS resolves",", ".join(addresses),"Review DNS changes as part of deployment monitoring.")]
