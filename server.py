import json,os
from http.server import HTTPServer,BaseHTTPRequestHandler
from datetime import datetime
D={}
class H(BaseHTTPRequestHandler):
 def log_message(self,f,*a):pass
 def c(self):
  self.send_header("Access-Control-Allow-Origin","*")
  self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
  self.send_header("Access-Control-Allow-Headers","Content-Type,*")
 def do_OPTIONS(self):
  self.send_response(200);self.c();self.end_headers()
 def do_POST(self):
  global D
  b=self.rfile.read(int(self.headers.get("Content-Length",0)))
  try:
   D=json.loads(b.decode("utf-8","replace").strip())
   D["received_at"]=datetime.now().isoformat()
   print(f"OK {len(D.get('systems',[]))} sistemas bal={D.get('balance',0)}")
  except Exception as e:print(f"ERR {e}")
  self.send_response(200);self.c();self.send_header("Content-Type","text/plain");self.end_headers();self.wfile.write(b"OK")
 def do_GET(self):
  if self.path=="/data":
   p=json.dumps(D) if D.get("systems") else json.dumps({"no_data":True,"systems":[],"balance":0,"equity":0})
   self.send_response(200);self.send_header("Content-Type","application/json");self.c();self.end_headers();self.wfile.write(p.encode())
  elif self.path=="/logs":
   info=f"systems:{len(D.get('systems',[]))}\nbalance:{D.get('balance',0)}\nreceived:{D.get('received_at','nunca')}\n"
   self.send_response(200);self.send_header("Content-Type","text/plain");self.c();self.end_headers();self.wfile.write(info.encode())
  elif self.path in["/","/index.html"]:
   try:
    with open("index.html","rb") as f:c=f.read()
    self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(c)
   except:self.send_response(503);self.end_headers();self.wfile.write(b"cargando...")
  else:self.send_response(404);self.end_headers()
port=int(os.environ.get("PORT",8080))
print(f"Puerto {port}")
HTTPServer(("0.0.0.0",port),H).serve_forever()
