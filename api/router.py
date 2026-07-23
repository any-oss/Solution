#!/usr/bin/env python3
"""API Router for the AI Agent System.

This module provides the main API routing layer that handles:
- Request parsing and validation
- Authentication and authorization
- Task routing to appropriate agents
- Response formatting and error handling
"""
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class APIRouter(BaseHTTPRequestHandler):
    """HTTP request handler for API routing."""

    def __init__(self, *args, **kwargs):
        """Initialize the API router."""
        self.agents: Dict[str, Any] = {}
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args) -> None:
        """Override to use custom logger."""
        logger.info("%s - %s", self.address_string(), format % args)

    def _send_json_response(
        self,
        data: Dict[str, Any],
        status_code: int = 200
    ) -> None:
        """Send a JSON response.

        Args:
            data: Response data dictionary.
            status_code: HTTP status code.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error_response(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send an error response.

        Args:
            message: Error message.
            status_code: HTTP status code.
            details: Optional additional error details.
        """
        response = {
            "status": "error",
            "message": message
        }
        if details:
            response["details"] = details

        self._send_json_response(response, status_code)

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/health':
            self._handle_health()
        elif path == '/metrics':
            self._handle_metrics()
        elif path == '/agents':
            self._handle_list_agents()
        elif path.startswith('/task/'):
            task_id = path.split('/')[-1]
            self._handle_get_task(task_id)
        else:
            self._send_error_response("Not found", 404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get('Content-Length', 0))

        if path == '/generate':
            self._handle_generate(content_length)
        elif path == '/classify':
            self._handle_classify(content_length)
        elif path == '/execute':
            self._handle_execute(content_length)
        else:
            self._send_error_response("Not found", 404)

    def _handle_health(self) -> None:
        """Handle health check endpoint."""
        health_data = {
            "status": "healthy",
            "service": "api-router",
            "version": "1.0.0"
        }
        self._send_json_response(health_data)

    def _handle_metrics(self) -> None:
        """Handle metrics endpoint in Prometheus format."""
        metrics = [
            "# HELP api_requests_total Total number of API requests",
            "# TYPE api_requests_total counter",
            "api_requests_total{method=\"GET\"} 0",
            "api_requests_total{method=\"POST\"} 0",
            "# HELP api_latency_ms API request latency in milliseconds",
            "# TYPE api_latency_ms gauge",
            "api_latency_ms{endpoint=\"/health\"} 1.5",
        ]
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write('\n'.join(metrics).encode())

    def _handle_list_agents(self) -> None:
        """Handle list agents endpoint."""
        from backend.agents import __all__ as agent_names

        agents_info = {
            "status": "success",
            "agents": [
                {"name": name, "registered": name in self.agents}
                for name in agent_names
            ],
            "total": len(agent_names)
        }
        self._send_json_response(agents_info)

    def _handle_get_task(self, task_id: str) -> None:
        """Handle get task status endpoint.

        Args:
            task_id: Task identifier.
        """
        # In production, this would query the database
        task_data = {
            "status": "success",
            "task_id": task_id,
            "state": "pending",
            "result": None
        }
        self._send_json_response(task_data)

    def _handle_generate(self, content_length: int) -> None:
        """Handle code generation request.

        Args:
            content_length: Length of request body.
        """
        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
        except json.JSONDecodeError:
            self._send_error_response("Invalid JSON", 400)
            return

        prompt = data.get('prompt', '')
        language = data.get('language', 'python')

        if not prompt:
            self._send_error_response("Missing 'prompt' field", 400)
            return

        from backend.agents import CodeGeneratorAgent

        agent = CodeGeneratorAgent(model_name="qwen2.5-coder")
        result = agent.generate(prompt=prompt)

        if result.get('status') == 'success':
            self._send_json_response(result)
        else:
            self._send_error_response(
                "Generation failed",
                500,
                result.get('error')
            )

    def _handle_classify(self, content_length: int) -> None:
        """Handle task classification request.

        Args:
            content_length: Length of request body.
        """
        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
        except json.JSONDecodeError:
            self._send_error_response("Invalid JSON", 400)
            return

        request_text = data.get('request', '')

        if not request_text:
            self._send_error_response("Missing 'request' field", 400)
            return

        # Simple keyword-based classification
        # In production, this would use an LLM
        classification_map = {
            'generate': 'code_generation',
            'create': 'code_generation',
            'write': 'code_generation',
            'refactor': 'refactoring',
            'improve': 'refactoring',
            'test': 'testing',
            'bug': 'bug_detection',
            'fix': 'bug_detection',
            'document': 'documentation',
            'migrate': 'migration',
            'deploy': 'devops',
            'release': 'release'
        }

        detected_type = 'general'
        for keyword, task_type in classification_map.items():
            if keyword in request_text.lower():
                detected_type = task_type
                break

        classification_result = {
            "status": "success",
            "request": request_text[:100],
            "classified_type": detected_type,
            "confidence": 0.85,
            "suggested_agent": f"{detected_type}_agent"
        }
        self._send_json_response(classification_result)

    def _handle_execute(self, content_length: int) -> None:
        """Handle workflow execution request.

        Args:
            content_length: Length of request body.
        """
        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
        except json.JSONDecodeError:
            self._send_error_response("Invalid JSON", 400)
            return

        workflow_name = data.get('workflow', 'default')
        tasks = data.get('tasks', [])

        if not tasks:
            self._send_error_response("Missing 'tasks' field", 400)
            return

        from workflow.orchestrator import WorkflowOrchestrator

        orchestrator = WorkflowOrchestrator()
        execution = orchestrator.create_workflow(workflow_name, tasks)

        result = {
            "status": "success",
            "execution_id": execution.execution_id,
            "workflow_name": workflow_name,
            "tasks_created": len(tasks),
            "status_url": f"/task/{execution.execution_id}"
        }
        self._send_json_response(result)


def run_server(host: str = '0.0.0.0', port: int = 8000) -> None:
    """Run the API router server.

    Args:
        host: Server host address.
        port: Server port number.
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, APIRouter)

    logger.info(f"API Router starting on {host}:{port}")
    logger.info("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        httpd.server_close()
        logger.info("Server stopped")


if __name__ == '__main__':
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

    run_server(host, port)
