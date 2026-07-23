"""Workflow orchestrator for multi-agent task coordination."""
import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a workflow task."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "general"
    status: str = "pending"
    priority: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error_message: Optional[str] = None
    assigned_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class WorkflowExecution:
    """Tracks a complete workflow execution."""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = ""
    status: str = "running"
    tasks: List[Task] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows with task routing and coordination.
    
    This class manages task distribution across specialized agents,
    handles dependencies between tasks, and tracks execution progress.
    """
    
    def __init__(self):
        """Initialize the Workflow Orchestrator."""
        self.executions: Dict[str, WorkflowExecution] = {}
        self.task_queue: List[Task] = []
        self.agents: Dict[str, Any] = {}
        logger.info("WorkflowOrchestrator initialized")
    
    def register_agent(self, name: str, agent_instance: Any) -> None:
        """Register an agent for task execution.
        
        Args:
            name: Unique identifier for the agent.
            agent_instance: The agent object instance.
        """
        self.agents[name] = agent_instance
        logger.info(f"Agent registered: {name}")
    
    def create_workflow(self, name: str, tasks: List[Dict[str, Any]]) -> WorkflowExecution:
        """Create a new workflow execution with tasks.
        
        Args:
            name: Name of the workflow.
            tasks: List of task definitions.
            
        Returns:
            Created workflow execution object.
        """
        logger.info(f"Creating workflow: {name} with {len(tasks)} tasks")
        
        execution = WorkflowExecution(workflow_name=name)
        
        for task_def in tasks:
            task = Task(
                type=task_def.get("type", "general"),
                priority=task_def.get("priority", 0),
                payload=task_def.get("payload", {}),
                assigned_agent=task_def.get("agent")
            )
            execution.tasks.append(task)
            self.task_queue.append(task)
        
        execution.total_tasks = len(execution.tasks)
        self.executions[execution.execution_id] = execution
        
        logger.info(f"Workflow created: {execution.execution_id}")
        return execution
    
    def route_task(self, task: Task) -> Optional[str]:
        """Determine which agent should handle a task.
        
        Args:
            task: Task to route.
            
        Returns:
            Name of the assigned agent or None if no suitable agent found.
        """
        if task.assigned_agent and task.assigned_agent in self.agents:
            return task.assigned_agent
        
        # Simple routing based on task type
        routing_map = {
            "code_generation": "code_generator",
            "refactoring": "refactoring",
            "testing": "testing",
            "bug_detection": "bug_detection",
            "documentation": "documentation",
            "migration": "migration",
            "devops": "devops",
            "release": "release"
        }
        
        agent_name = routing_map.get(task.type)
        if agent_name and agent_name in self.agents:
            return agent_name
        
        # Default to first available agent
        if self.agents:
            return next(iter(self.agents.keys()))
        
        return None
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task using the assigned agent.
        
        Args:
            task: Task to execute.
            
        Returns:
            Task execution result.
        """
        logger.info(f"Executing task {task.task_id} (type: {task.type})")
        
        task.started_at = datetime.utcnow().isoformat()
        task.status = "running"
        
        agent_name = self.route_task(task)
        if not agent_name:
            task.status = "failed"
            task.error_message = "No suitable agent found"
            task.completed_at = datetime.utcnow().isoformat()
            return {"status": "failed", "error": "No agent available"}
        
        task.assigned_agent = agent_name
        agent = self.agents[agent_name]
        
        try:
            # Execute based on task type
            if task.type == "code_generation":
                result = agent.generate(prompt=task.payload.get("prompt", ""))
            elif task.type == "testing":
                result = agent.generate_tests(code=task.payload.get("code", ""))
            elif task.type == "bug_detection":
                result = agent.scan(code=task.payload.get("code", ""))
            else:
                result = {"status": "success", "data": task.payload}
            
            task.status = "completed"
            task.result = result
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            result = {"status": "failed", "error": str(e)}
            logger.error(f"Task {task.task_id} failed: {e}")
        
        finally:
            task.completed_at = datetime.utcnow().isoformat()
        
        return result
    
    def execute_workflow(self, execution_id: str) -> Dict[str, Any]:
        """Execute all tasks in a workflow.
        
        Args:
            execution_id: ID of the workflow execution.
            
        Returns:
            Workflow execution results.
        """
        if execution_id not in self.executions:
            return {"status": "error", "message": "Workflow not found"}
        
        execution = self.executions[execution_id]
        logger.info(f"Executing workflow: {execution.workflow_name}")
        
        completed = 0
        failed = 0
        
        for task in execution.tasks:
            result = self.execute_task(task)
            if result.get("status") == "failed":
                failed += 1
            else:
                completed += 1
        
        execution.completed_tasks = completed
        execution.failed_tasks = failed
        execution.status = "completed" if failed == 0 else "partially_completed"
        execution.completed_at = datetime.utcnow().isoformat()
        
        logger.info(f"Workflow {execution_id} completed: {completed}/{len(execution.tasks)} tasks successful")
        
        return {
            "status": "success",
            "execution_id": execution_id,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "total_tasks": len(execution.tasks)
        }
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution.
            
        Returns:
            Current execution status.
        """
        if execution_id not in self.executions:
            return {"status": "error", "message": "Workflow not found"}
        
        execution = self.executions[execution_id]
        
        return {
            "execution_id": execution_id,
            "workflow_name": execution.workflow_name,
            "status": execution.status,
            "total_tasks": len(execution.tasks),
            "completed_tasks": execution.completed_tasks,
            "failed_tasks": execution.failed_tasks,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at
        }
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks in the queue.
        
        Returns:
            List of pending tasks.
        """
        return [t for t in self.task_queue if t.status == "pending"]
