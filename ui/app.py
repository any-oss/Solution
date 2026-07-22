"""UI Dashboard for monitoring the AI Proxy service.

This module provides a web-based dashboard for:
- Real-time health monitoring
- Prometheus metrics visualization
- Database analytics display
- Request traffic inspection
"""
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional

import requests

from core.database import get_database, close_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_proxy_url() -> str:
    """Get the proxy URL from environment or use default.
    
    Returns:
        Proxy server URL.
    """
    import os
    return os.getenv("PROXY_URL", "http://localhost:8000")


class UIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the UI dashboard."""

    def __init__(self, *args: Any, proxy_url: Optional[str] = None, **kwargs: Any) -> None:
        self._proxy_url = proxy_url
        super().__init__(*args, **kwargs)

    @property
    def proxy_url(self) -> str:
        """Get the proxy URL."""
        return self._proxy_url if self._proxy_url else get_proxy_url()

    def _send_html_response(self, status_code: int, html: str) -> None:
        """Send an HTML response.
        
        Args:
            status_code: HTTP status code.
            html: HTML content to send.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send a JSON response.
        
        Args:
            status_code: HTTP status code.
            data: Data to serialize as JSON.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _fetch_health(self) -> Dict[str, Any]:
        """Fetch health status from the proxy."""
        try:
            resp = requests.get(f"{self.proxy_url}/health", timeout=2)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {"status": "unreachable"}

    def _fetch_metrics(self) -> str:
        """Fetch metrics from the proxy."""
        try:
            resp = requests.get(f"{self.proxy_url}/metrics", timeout=2)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return ""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/":
            health = self._fetch_health()
            metrics = self._fetch_metrics()
            
            # Fetch database analytics
            try:
                db = get_database()
                analytics = db.get_analytics(hours=24)
                recent_requests = db.get_recent_requests(limit=10)
            except Exception as e:
                logger.warning(f"Failed to fetch database analytics: {e}")
                analytics = {}
                recent_requests = []

            html = f"""<!DOCTYPE html>
<html><head><title>AI Proxy Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
.card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
h1 {{ color: #333; }}
h2 {{ color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
.stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
.stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
.stat-value {{ font-size: 2em; color: #007bff; font-weight: bold; }}
.stat-label {{ color: #666; margin-top: 5px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
th {{ background: #f8f9fa; }}
.status-healthy {{ color: #28a745; }}
.status-error {{ color: #dc3545; }}
</style>
</head>
<body>
<div class="container">
    <h1>🚀 AI Proxy Dashboard</h1>
    
    <div class="card">
        <h2>System Health</h2>
        <pre class="{'status-healthy' if health.get('status') == 'healthy' else 'status-error'}">{json.dumps(health, indent=2)}</pre>
    </div>
    
    <div class="card">
        <h2>📊 Analytics (Last 24 Hours)</h2>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{analytics.get('total_requests', 0)}</div>
                <div class="stat-label">Total Requests</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{analytics.get('cpu_requests', 0)}</div>
                <div class="stat-label">CPU Backend</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{analytics.get('gpu_requests', 0)}</div>
                <div class="stat-label">GPU Backend</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{analytics.get('error_rate_percent', 0)}%</div>
                <div class="stat-label">Error Rate</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{analytics.get('active_sessions', 0)}</div>
                <div class="stat-label">Active Sessions</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>📋 Recent Requests</h2>
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Backend</th>
                    <th>Latency (ms)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''<tr>
                    <td>{r.get('timestamp', 'N/A')}</td>
                    <td>{r.get('method', 'N/A')}</td>
                    <td>{r.get('endpoint', 'N/A')}</td>
                    <td>{r.get('backend', 'N/A')}</td>
                    <td>{r.get('latency_ms', 0):.2f}</td>
                    <td class="{'status-healthy' if r.get('status_code', 0) < 400 else 'status-error'}">{r.get('status_code', 'N/A')}</td>
                </tr>''' for r in recent_requests) or '<tr><td colspan="6">No recent requests</td></tr>'}
            </tbody>
        </table>
    </div>
    
    <div class="card">
        <h2>📈 Raw Prometheus Metrics</h2>
        <pre>{metrics}</pre>
    </div>
</div>
</body></html>"""
            self._send_html_response(200, html)
        elif self.path == "/api/analytics":
            # API endpoint for analytics data
            try:
                db = get_database()
                analytics = db.get_analytics(hours=24)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(analytics).encode())
            except Exception as e:
                logger.error(f"Failed to fetch analytics: {e}")
                self._send_json_response(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        """Log HTTP request messages."""
        logger.info("%s - %s", self.client_address[0], format % args)


def run_server(host: str = '0.0.0.0', port: int = 8080) -> None:
    """Run the UI dashboard server.
    
    Args:
        host: Host address to bind to.
        port: Port number to listen on.
    """
    # Initialize database connection
    try:
        get_database()
        logger.info("Database initialized for dashboard")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
    
    server = HTTPServer((host, port), UIHandler)
    logger.info(f"UI Dashboard on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        close_database()


if __name__ == "__main__":
    run_server()
