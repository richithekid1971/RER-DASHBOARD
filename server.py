import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DATA_FILE = "/tmp/rer.json"
latest_data = None

def load():
    global latest_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                latest_data = json.load(f)
            print(f"Datos cargados de disco: {len(latest_data.get('systems',[]))} sistemas")
    except Exception as e:
        print(f"Error cargando: {e}")

def save(d):
    try:
        with open(DATA_FILE,'w') as f:
            json.dump(d, f)
    except Exception as e:
        print(f"Error guardando: {e}")

load()

class H(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type,*")

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_POST(self):
        global latest_data
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length)
        raw = body.decode("utf-8","replace").strip()
        print(f"\n[POST {datetime.now().strftime('%H:%M:%S')}] {length} bytes")
        print(f"Primeros 200 chars: {raw[:200]}")
        try:
            data = json.loads(raw)
            data["received_at"] = datetime.now().isoformat()
            latest_data = data
            save(data)
            n = len(data.get("systems",[]))
            print(f"OK — {n} sistemas | balance={data.get('balance',0)}")
        except Exception as e:
            print(f"ERROR JSON: {e}")
            print(f"Raw completo: {raw}")
        self.send_response(200)
        self.cors()
        self.send_header("Content-Type","text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        if self.path == "/data":
            if latest_data and latest_data.get("systems"):
                payload = json.dumps(latest_data)
                print(f"[GET /data] Sirviendo {len(latest_data['systems'])} sistemas")
            else:
                payload = json.dumps({"no_data":True,"systems":[],"balance":0,"equity":0})
                print(f"[GET /data] Sin datos aun")
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.cors()
            self.end_headers()
            self.wfile.write(payload.encode())
        elif self.path in ["/","/index.html"]:
            try:
                with open("index.html","rb") as f: c=f.read()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(c)
            except:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"<h1>Cargando...</h1>")
        elif self.path == "/logs":
            # Endpoint para ver logs en tiempo real
            self.send_response(200)
            self.send_header("Content-Type","text/plain; charset=utf-8")
            self.cors()
            self.end_headers()
            info = f"latest_data is None: {latest_data is None}\n"
            if latest_data:
                info += f"systems count: {len(latest_data.get('systems',[]))}\n"
                info += f"balance: {latest_data.get('balance',0)}\n"
                info += f"received_at: {latest_data.get('received_at','?')}\n"
            self.wfile.write(info.encode())
        else:
            self.send_response(404)
            self.end_headers()

port = int(os.environ.get("PORT",8080))
print(f"RER Dashboard arrancando en puerto {port}")
HTTPServer(("0.0.0.0",port),H).serve_forever()
