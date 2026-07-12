from __future__ import annotations
import json
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from config.settings import PORT,ROOT
from database.store import Store
class Dashboard(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def do_GET(self):
  if self.path=="/api/runs":return self.json(Store().recent())
  if self.path=="/api/metrics":return self.json(Store().metrics())
  if self.path=="/":self.path="/dashboard/index.html"
  return super().do_GET()
 def json(self,data):
  body=json.dumps(data).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,format,*args):print("dashboard:",format%args)
def serve(port=None):
 address=("127.0.0.1",port or PORT);print(f"Dashboard: http://{address[0]}:{address[1]}");ThreadingHTTPServer(address,Dashboard).serve_forever()
