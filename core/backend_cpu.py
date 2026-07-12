import json
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from core.config import HOST, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

class CPUHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "backend": "cpu"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        start = time.time()
        time.sleep(0.1)
        response = {"backend": "cpu", "result": f"processed in {time.time()-start:.3f}s"}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    server = HTTPServer((HOST, 8001), CPUHandler)
    logger.info("CPU backend on port 8001")
    server.serve_forever()
