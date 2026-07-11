#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            response = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "proxy"
            }
            self.send_response(200)
        else:
            response = {"status": "ok", "path": self.path}
            self.send_response(200)
        
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        response = {"status": "ok", "method": "POST"}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    logger.info(f"Proxy server starting on port {port}")
    server.serve_forever()
