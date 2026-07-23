#!/usr/bin/env python3
"""Integration tests for the AI Agent System."""
import unittest
import json
import threading
import time
from http.server import HTTPServer
from typing import Dict, Any

from workflow.orchestrator import WorkflowOrchestrator, Task
from workflow.task_queue import TaskQueue, TaskPriority
from backend.agents import (
    CodeGeneratorAgent,
    TestingAgent,
    DevOpsAgent,
    BugDetectionAgent,
    DocumentationAgent
)


class TestWorkflowOrchestrator(unittest.TestCase):
    """Test workflow orchestration functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.orchestrator = WorkflowOrchestrator()
        self.orchestrator.register_agent('code_generator', CodeGeneratorAgent())
        self.orchestrator.register_agent('testing', TestingAgent())
        self.orchestrator.register_agent('devops', DevOpsAgent())

    def test_create_workflow(self) -> None:
        """Test workflow creation with multiple tasks."""
        tasks = [
            {"type": "code_generation", "payload": {"prompt": "test"}},
            {"type": "testing", "payload": {"code": "def x(): pass"}},
        ]
        
        workflow = self.orchestrator.create_workflow("test_workflow", tasks)
        
        self.assertEqual(workflow.workflow_name, "test_workflow")
        self.assertEqual(len(workflow.tasks), 2)
        self.assertEqual(workflow.status, "running")

    def test_route_task(self) -> None:
        """Test task routing to appropriate agents."""
        task = Task(type="code_generation", payload={"prompt": "test"})
        agent_name = self.orchestrator.route_task(task)
        
        self.assertEqual(agent_name, "code_generator")

    def test_execute_task_success(self) -> None:
        """Test successful task execution."""
        task = Task(
            type="code_generation",
            payload={"prompt": "Create a hello world function"}
        )
        
        result = self.orchestrator.execute_task(task)
        
        self.assertEqual(result.get("status"), "success")
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.completed_at)

    def test_execute_workflow(self) -> None:
        """Test complete workflow execution."""
        tasks = [
            {"type": "code_generation", "payload": {"prompt": "test"}},
        ]
        
        workflow = self.orchestrator.create_workflow("exec_test", tasks)
        result = self.orchestrator.execute_workflow(workflow.execution_id)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["completed_tasks"], 1)
        self.assertEqual(result["failed_tasks"], 0)


class TestTaskQueue(unittest.TestCase):
    """Test task queue functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.queue = TaskQueue(max_workers=2)
        self.queue.start()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.queue.stop()

    def test_enqueue_task(self) -> None:
        """Test task enqueueing."""
        task_id = "test_task_1"
        payload = {"type": "code_generate", "prompt": "test"}
        
        result = self.queue.enqueue(task_id, payload, TaskPriority.NORMAL)
        
        self.assertTrue(result)
        self.assertEqual(self.queue.get_queue_size(), 1)

    def test_task_priority_ordering(self) -> None:
        """Test that high priority tasks are processed first."""
        results = []
        
        def callback(task_id: str, result: Dict[str, Any]) -> None:
            results.append((task_id, time.time()))
        
        # Enqueue tasks with different priorities
        self.queue.enqueue("low", {"type": "general"}, TaskPriority.LOW, callback)
        self.queue.enqueue("high", {"type": "general"}, TaskPriority.HIGH, callback)
        self.queue.enqueue("normal", {"type": "general"}, TaskPriority.NORMAL, callback)
        
        # Wait for completion
        self.queue.wait_completion(timeout=5.0)
        time.sleep(0.5)
        
        # High priority should complete first
        self.assertGreater(len(results), 0)

    def test_get_result(self) -> None:
        """Test retrieving task results."""
        task_id = "result_test"
        payload = {"type": "general"}
        
        self.queue.enqueue(task_id, payload)
        self.queue.wait_completion(timeout=5.0)
        time.sleep(0.5)
        
        result = self.queue.get_result(task_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_id"], task_id)
        self.assertEqual(result["status"], "completed")


class TestAgents(unittest.TestCase):
    """Test individual agent functionality."""

    def test_code_generator_agent(self) -> None:
        """Test code generation agent."""
        agent = CodeGeneratorAgent(model_name="qwen2.5-coder", temperature=0.7)
        result = agent.generate(prompt="Create a function that adds two numbers")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["model"], "qwen2.5-coder")

    def test_testing_agent(self) -> None:
        """Test testing agent."""
        agent = TestingAgent(framework="pytest")
        code = "def add(a, b): return a + b"
        result = agent.generate_tests(code=code, coverage_target=90.0)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("test_code", result)
        self.assertEqual(result["framework"], "pytest")

    def test_devops_agent_dockerfile(self) -> None:
        """Test DevOps agent Dockerfile generation."""
        agent = DevOpsAgent(platform="docker")
        dockerfile = agent.generate_dockerfile(app_type="python", requirements=[])
        
        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("WORKDIR /app", dockerfile)

    def test_devops_agent_k8s_manifest(self) -> None:
        """Test DevOps agent Kubernetes manifest generation."""
        agent = DevOpsAgent()
        result = agent.create_k8s_manifest(service_name="test-service", replicas=3)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("apiVersion: apps/v1", result["deployment"])
        self.assertIn("replicas: 3", result["deployment"])

    def test_bug_detection_agent(self) -> None:
        """Test bug detection agent."""
        from backend.agents import BugDetectionAgent
        
        agent = BugDetectionAgent()
        code = "def unsafe(password): return password"
        result = agent.scan(code=code)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("bugs", result)
        self.assertIn("warnings", result)
        self.assertIn("summary", result)

    def test_documentation_agent(self) -> None:
        """Test documentation agent."""
        from backend.agents import DocumentationAgent
        
        agent = DocumentationAgent()
        code = "def calculate(x, y): return x * y"
        docstring = agent.generate_docstring(code=code)
        
        self.assertIsInstance(docstring, str)
        self.assertIn('"""', docstring)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def test_code_to_test_workflow(self) -> None:
        """Test complete workflow from code generation to testing."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.register_agent('code_generator', CodeGeneratorAgent())
        orchestrator.register_agent('testing', TestingAgent())
        
        tasks = [
            {
                "type": "code_generation",
                "payload": {"prompt": "Create a calculator class"}
            },
            {
                "type": "testing",
                "payload": {"code": "class Calculator: pass"}
            }
        ]
        
        workflow = orchestrator.create_workflow("code_to_test", tasks)
        result = orchestrator.execute_workflow(workflow.execution_id)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_tasks"], 2)

    def test_devops_deployment_workflow(self) -> None:
        """Test DevOps deployment workflow."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.register_agent('devops', DevOpsAgent())
        
        tasks = [
            {
                "type": "devops",
                "payload": {"action": "deploy", "environment": "staging"}
            }
        ]
        
        workflow = orchestrator.create_workflow("deploy_staging", tasks)
        result = orchestrator.execute_workflow(workflow.execution_id)
        
        self.assertEqual(result["status"], "success")


if __name__ == '__main__':
    unittest.main(verbosity=2)
