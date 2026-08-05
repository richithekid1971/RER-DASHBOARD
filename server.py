import json, time, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

latest_data = {"account":"","timestamp":0,"balance":0,"equity":0,"systems":[]}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
    def do_POST(self):
        global latest_data
        if self.path=="/update":
            length = int(self.headers.get("Content-Length",0))
            body = self.rfile.read(length)
            try:
                text = body.decode("utf-8", errors="replace")
                latest_data = json.loads(text)
                latest_data["received_at"] = datetime.now().isoformat()
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin","*")
                self.send_header("Content-Type","text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
            except Exception as e:
                print("Error parsing JSON:", e, "Body:", body[:200])
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(b"OK")
    def do_GET(self):
        if self.path=="/data":
            data=json.dumps(latest_data).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(data)
        elif self.path in["/","index.html","/index.html"]:
            try:
                with open("index.html","rb") as f: content=f.read()
            except:
                content=b"<h1>Dashboard loading...</h1>"
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

port=int(os.environ.get("PORT",8080))
print(f"Servidor arrancando en puerto {port}")
HTTPServer(("0.0.0.0",port),Handler).serve_forever()
