import unittest
import threading
import urllib.request
import json
from http.server import HTTPServer
from core.proxy import ProxyHandler

class TestProxy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('localhost', 0), ProxyHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_health(self):
        resp = urllib.request.urlopen(f"http://localhost:{self.port}/health")
        self.assertEqual(resp.status, 200)
        data = json.loads(resp.read())
        self.assertEqual(data["status"], "healthy")

    def test_metrics_endpoint(self):
        resp = urllib.request.urlopen(f"http://localhost:{self.port}/metrics")
        self.assertIn("http_requests_total", resp.read().decode())

    def test_post_routing(self):
        data = json.dumps({"prompt": "short"}).encode()
        req = urllib.request.Request(f"http://localhost:{self.port}/generate",
                                     data=data,
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req)
        self.assertEqual(resp.status, 200)

if __name__ == "__main__":
    unittest.main()
