from __future__ import annotations
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse
from agents.security_agent import SecurityBarbie
from config.settings import ALLOWED_TARGETS,PORT,ROOT
from database.store import Store
class Dashboard(BaseHTTPRequestHandler):
 def do_GET(self):
  path=urlparse(self.path).path
  if path=="/api/runs":return self.json(Store().recent())
  if path=="/api/metrics":return self.json(Store().metrics())
  if path=="/api/agent":return self.json({"name":"Security Agent","allowed_targets":sorted(ALLOWED_TARGETS)})
  if path=="/":return self.file(ROOT/"dashboard"/"security.html","text/html; charset=utf-8")
  return self.send_error(HTTPStatus.NOT_FOUND,"Not found")
 def do_POST(self):
  if urlparse(self.path).path!="/api/scans":return self.send_error(HTTPStatus.NOT_FOUND,"Not found")
  try:
   size=int(self.headers.get("Content-Length","0"))
   if not 0<size<=4096:raise ValueError("Invalid request size")
   target=str(json.loads(self.rfile.read(size)).get("target",""))
   run=SecurityBarbie().run(target)
  except PermissionError as exc:return self.json({"error":str(exc)},HTTPStatus.FORBIDDEN)
  except (ValueError,json.JSONDecodeError) as exc:return self.json({"error":str(exc)},HTTPStatus.BAD_REQUEST)
  except Exception:return self.json({"error":"Scan failed. Review the server log."},HTTPStatus.INTERNAL_SERVER_ERROR)
  return self.json({"run_id":run.run_id,"status":run.status},HTTPStatus.ACCEPTED)
 def file(self,path,content_type):
  if not path.is_file():return self.send_error(HTTPStatus.NOT_FOUND,"Not found")
  body=path.read_bytes();self.send_response(HTTPStatus.OK);self.send_header("Content-Type",content_type);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
 def json(self,data,status=HTTPStatus.OK):
  body=json.dumps(data).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,format,*args):print("dashboard:",format%args)
def serve(port=None):
 address=("127.0.0.1",port or PORT);print(f"Dashboard: http://{address[0]}:{address[1]}");ThreadingHTTPServer(address,Dashboard).serve_forever()
