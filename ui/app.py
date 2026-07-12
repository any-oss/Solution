import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PROXY_URL = os.getenv("PROXY_URL", "http://localhost:8000")

class UIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            try:
                health = requests.get(f"{PROXY_URL}/health", timeout=2).json()
                metrics = requests.get(f"{PROXY_URL}/metrics", timeout=2).text
            except Exception:
                health = {"status": "unreachable"}
                metrics = ""
            html = f"""<!DOCTYPE html>
<html><head><title>AI Proxy Dashboard</title></head>
<body>
    <h1>AI Proxy Status</h1>
    <pre>{json.dumps(health, indent=2)}</pre>
    <h2>Raw Metrics</h2>
    <pre>{metrics}</pre>
</body></html>"""
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), UIHandler)
    logger.info("UI Dashboard on port 8080")
    server.serve_forever()
