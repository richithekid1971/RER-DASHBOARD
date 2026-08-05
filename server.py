import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DATA_FILE = "/tmp/rer_data.json"
latest_data = None

def load():
    global latest_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                latest_data = json.load(f)
    except: pass

def save(data):
    try:
        with open(DATA_FILE,'w') as f:
            json.dump(data, f)
    except: pass

load()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_POST(self):
        global latest_data
        if self.path == "/update":
            body = self.rfile.read(int(self.headers.get("Content-Length",0)))
            try:
                data = json.loads(body.decode("utf-8","replace").strip())
                data["received_at"] = datetime.now().isoformat()
                latest_data = data
                save(data)
                n = len(data.get("systems",[]))
                bal = data.get("balance",0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {n} sistemas | bal={bal}")
            except Exception as e:
                print(f"[ERR] {e}")
            self.send_response(200)
            self.cors()
            self.send_header("Content-Type","text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

    def do_GET(self):
        if self.path == "/data":
            payload = json.dumps(latest_data) if latest_data else json.dumps({"no_data":True,"systems":[],"balance":0,"equity":0})
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.cors()
            self.end_headers()
            self.wfile.write(payload.encode())

        elif self.path in ["/","/index.html"]:
            try:
                with open("index.html","rb") as f: content=f.read()
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

port = int(os.environ.get("PORT",8080))
print(f"RER Dashboard — puerto {port}")
HTTPServer(("0.0.0.0",port),Handler).serve_forever()
