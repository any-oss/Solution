"""CPU backend server for processing short prompts."""
import json
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict

from core.config import HOST, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)


class CPUHandler(BaseHTTPRequestHandler):
    """HTTP request handler for CPU backend."""

    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send a JSON response with the given status code and data."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self._send_json_response(200, {"status": "healthy", "backend": "cpu"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests by processing with simulated delay."""
        start = time.time()
        time.sleep(0.1)
        response = {
            "backend": "cpu",
            "result": f"processed in {time.time()-start:.3f}s"
        }
        self._send_json_response(200, response)

    def log_message(self, format: str, *args: Any) -> None:
        """Log HTTP request messages."""
        logger.info("%s - %s", self.client_address[0], format % args)


def run_server(host: str = HOST, port: int = 8001) -> None:
    """Run the CPU backend server."""
    server = HTTPServer((host, port), CPUHandler)
    logger.info(f"CPU backend on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
