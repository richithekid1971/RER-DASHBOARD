import json, time, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

latest_data = None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")

    def do_POST(self):
        global latest_data
        if self.path == "/update":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                text = body.decode("utf-8", errors="replace").strip()
                data = json.loads(text)
                data["received_at"] = datetime.now().isoformat()
                latest_data = data
                print(f"[{datetime.now().strftime('%H:%M:%S')}] OK — {len(data.get('systems',[]))} sistemas | bal={data.get('balance',0)}")
            except Exception as e:
                print(f"[ERROR] {e} | body={body[:100]}")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type","text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

    def do_GET(self):
        if self.path == "/data":
            if latest_data:
                payload = json.dumps(latest_data)
            else:
                payload = json.dumps({"account":"","timestamp":0,"balance":0,"equity":0,"systems":[],"no_data":True})
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(payload.encode())

        elif self.path in ["/", "/index.html"]:
            try:
                with open("index.html","rb") as f: content = f.read()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"<h1>Loading...</h1>")
        else:
            self.send_response(404)
            self.end_headers()

port = int(os.environ.get("PORT", 8080))
print(f"RER Dashboard Server — puerto {port}")
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
