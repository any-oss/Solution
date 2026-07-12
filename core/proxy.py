import asyncio
import aiohttp
import json
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from core.config import HOST, PORT, CPU_BACKEND_URL, GPU_BACKEND_URL, LOG_LEVEL, HEALTH_CHECK_PATH
from core.metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_data, metrics_content_type

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.time()
        if self.path == HEALTH_CHECK_PATH:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "proxy"}).encode())
        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header('Content-Type', metrics_content_type())
            self.end_headers()
            self.wfile.write(metrics_data())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())
        REQUEST_COUNT.labels(method='GET', endpoint=self.path, status=200).inc()
        REQUEST_LATENCY.labels(endpoint=self.path).observe(time.time() - start)

    def do_POST(self):
        start = time.time()
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"
        payload = json.loads(body)
        prompt = payload.get("prompt", "")

        if len(prompt) > 100:
            backend_url = GPU_BACKEND_URL
        else:
            backend_url = CPU_BACKEND_URL

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(self._forward(backend_url, payload))
            status_code = 200
        except Exception as e:
            logger.error(f"Forwarding failed: {e}")
            response = {"error": "backend unavailable"}
            status_code = 502
        finally:
            loop.close()

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        REQUEST_COUNT.labels(method='POST', endpoint=self.path, status=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=self.path).observe(time.time() - start)

    async def _forward(self, url, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                return await resp.json()

    def log_message(self, format, *args):
        logger.info("%s - %s", self.client_address[0], format % args)

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), ProxyHandler)
    logger.info(f"Proxy serving on {HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
