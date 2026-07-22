"""Unit tests for the proxy server."""
import json
import threading
import unittest
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict
from unittest.mock import patch, MagicMock

from core.proxy import ProxyHandler


class MockBackendHandler(BaseHTTPRequestHandler):
    """Mock backend server for testing."""
    
    def do_POST(self) -> None:
        """Handle POST requests with mock response."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"result": "mocked response", "input": body}
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args) -> None:
        """Suppress logging."""
        pass


class TestProxy(unittest.TestCase):
    """Test cases for the ProxyHandler."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test servers."""
        # Start mock backend server
        cls.backend_server = HTTPServer(('localhost', 0), MockBackendHandler)
        cls.backend_port = cls.backend_server.server_address[1]
        cls.backend_thread = threading.Thread(target=cls.backend_server.serve_forever)
        cls.backend_thread.daemon = True
        cls.backend_thread.start()
        
        # Start proxy server
        cls.proxy_server = HTTPServer(('localhost', 0), ProxyHandler)
        cls.proxy_port = cls.proxy_server.server_address[1]
        cls.proxy_thread = threading.Thread(target=cls.proxy_server.serve_forever)
        cls.proxy_thread.daemon = True
        cls.proxy_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down test servers."""
        cls.proxy_server.shutdown()
        cls.backend_server.shutdown()

    def _fetch_json(self, path: str) -> Dict[str, Any]:
        """Fetch JSON response from the given path."""
        url = f"http://localhost:{self.proxy_port}{path}"
        resp = urllib.request.urlopen(url)
        return json.loads(resp.read())

    def test_health_endpoint(self) -> None:
        """Test health check endpoint returns healthy status."""
        data = self._fetch_json("/health")
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "proxy")

    def test_metrics_endpoint(self) -> None:
        """Test metrics endpoint returns Prometheus format data."""
        url = f"http://localhost:{self.proxy_port}/metrics"
        resp = urllib.request.urlopen(url)
        content = resp.read().decode()
        self.assertIn("http_requests_total", content)

    def test_not_found_endpoint(self) -> None:
        """Test unknown endpoint returns 404."""
        url = f"http://localhost:{self.proxy_port}/unknown"
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(url)
        self.assertEqual(context.exception.code, 404)

    def test_post_routing_short_prompt(self) -> None:
        """Test POST request with short prompt routes correctly."""
        data = json.dumps({"prompt": "short"}).encode()
        req = urllib.request.Request(
            f"http://localhost:{self.proxy_port}/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        self.assertEqual(resp.status, 200)

    def test_post_routing_long_prompt(self) -> None:
        """Test POST request with long prompt routes correctly."""
        long_prompt = "x" * 150
        data = json.dumps({"prompt": long_prompt}).encode()
        req = urllib.request.Request(
            f"http://localhost:{self.proxy_port}/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req)
        self.assertEqual(resp.status, 200)

    def test_post_invalid_json(self) -> None:
        """Test POST request with invalid JSON returns 400."""
        data = b"not valid json"
        req = urllib.request.Request(
            f"http://localhost:{self.proxy_port}/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
