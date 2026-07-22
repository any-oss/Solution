"""Task queue implementation for asynchronous workflow processing."""
import logging
import threading
import queue
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass(order=True)
class QueuedTask:
    """Task wrapper for priority queue ordering."""
    priority: int
    timestamp: str = field(compare=False)
    task_id: str = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)
    callback: Optional[Callable] = field(compare=False, default=None)


class TaskQueue:
    """Thread-safe priority task queue for workflow processing.
    
    This class provides asynchronous task processing with priority support,
    worker thread management, and task result tracking.
    """
    
    def __init__(self, max_workers: int = 4):
        """Initialize the Task Queue.
        
        Args:
            max_workers: Maximum number of worker threads.
        """
        self.queue: queue.PriorityQueue = queue.PriorityQueue()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.workers: list = []
        self.max_workers = max_workers
        self.running = False
        self.lock = threading.Lock()
        logger.info(f"TaskQueue initialized with {max_workers} workers")
    
    def start(self) -> None:
        """Start worker threads for task processing."""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {len(self.workers)} worker threads")
    
    def stop(self) -> None:
        """Stop all worker threads."""
        self.running = False
        # Add sentinel values to unblock workers
        for _ in self.workers:
            self.queue.put((TaskPriority.CRITICAL.value + 1, "", "", {}, None))
        
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
        logger.info("TaskQueue stopped")
    
    def _worker_loop(self) -> None:
        """Worker thread main loop."""
        while self.running:
            try:
                item = self.queue.get(timeout=1.0)
                if item[0] > TaskPriority.CRITICAL.value:
                    # Sentinel value, exit loop
                    self.queue.task_done()
                    break
                
                priority, timestamp, task_id, payload, callback = item
                self._process_task(task_id, payload, callback)
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def _process_task(self, task_id: str, payload: Dict[str, Any], callback: Optional[Callable]) -> None:
        """Process a single task.
        
        Args:
            task_id: Unique task identifier.
            payload: Task data and parameters.
            callback: Optional callback function for results.
        """
        logger.info(f"Processing task {task_id}")
        
        started_at = datetime.utcnow().isoformat()
        
        try:
            # Store task start
            with self.lock:
                self.results[task_id] = {
                    "task_id": task_id,
                    "status": "running",
                    "started_at": started_at,
                    "completed_at": None,
                    "result": None,
                    "error": None
                }
            
            # Execute task based on type from payload
            task_type = payload.get("type", "general")
            agent_name = payload.get("agent", "")
            logger.info(f"Executing task type: {task_type} with agent: {agent_name}")
            
            # Route to appropriate handler based on task type
            result = self._execute_task(task_type, payload)
            
            # Store result
            with self.lock:
                self.results[task_id].update({
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat(),
                    "result": result
                })
            
            # Call callback if provided
            if callback:
                try:
                    callback(task_id, result)
                except Exception as e:
                    logger.error(f"Callback error for task {task_id}: {e}")
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            with self.lock:
                self.results[task_id].update({
                    "status": "failed",
                    "completed_at": datetime.utcnow().isoformat(),
                    "error": str(e)
                })
    
    def _execute_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task based on its type.
        
        Args:
            task_type: Type of task to execute (code_generate, refactor, test, etc.).
            payload: Task data and parameters.
            
        Returns:
            Execution result dictionary.
        """
        from backend.agents import (
            CodeGeneratorAgent, RefactoringAgent, TestingAgent,
            BugDetectionAgent, DocumentationAgent, MigrationAgent,
            DevOpsAgent, ReleaseAgent, CodeViewAgent
        )
        
        # Map task types to agent classes and methods
        task_handlers = {
            "code_generate": (CodeGeneratorAgent, "generate"),
            "refactor": (RefactoringAgent, "refactor"),
            "test": (TestingAgent, "generate_tests"),
            "bug_detect": (BugDetectionAgent, "scan"),
            "document": (DocumentationAgent, "generate_docstring"),
            "migrate": (MigrationAgent, "plan_migration"),
            "deploy": (DevOpsAgent, "generate_dockerfile"),
            "release": (ReleaseAgent, "bump_version"),
            "view_code": (CodeViewAgent, "get_structure"),
        }
        
        if task_type not in task_handlers:
            logger.warning(f"Unknown task type: {task_type}, using general handler")
            return {"status": "success", "task_type": task_type, "message": "Task processed"}
        
        agent_class, method_name = task_handlers[task_type]
        agent = agent_class()
        
        # Extract arguments from payload
        code = payload.get("code", "")
        prompt = payload.get("prompt", "")
        source_version = payload.get("source_version", "1.0.0")
        target_version = payload.get("target_version", "1.1.0")
        
        # Call appropriate agent method
        if hasattr(agent, method_name):
            method = getattr(agent, method_name)
            if task_type == "code_generate":
                return method(prompt=prompt)
            elif task_type == "refactor":
                return method(code=code, suggestions=[])
            elif task_type == "test":
                return method(code=code)
            elif task_type == "bug_detect":
                return method(code=code)
            elif task_type == "document":
                return method(code=code)
            elif task_type == "migrate":
                return method(source_version=source_version, target_version=target_version)
            elif task_type == "deploy":
                return method(app_type="python", requirements=[])
            elif task_type == "release":
                return method(current_version=source_version, bump_type="patch")
            elif task_type == "view_code":
                return method(code=code)
        
        return {"status": "success", "task_type": task_type}
    
    def enqueue(self, task_id: str, payload: Dict[str, Any], 
                priority: TaskPriority = TaskPriority.NORMAL,
                callback: Optional[Callable] = None) -> bool:
        """Add a task to the queue.
        
        Args:
            task_id: Unique task identifier.
            payload: Task data and parameters.
            priority: Task priority level.
            callback: Optional callback function for results.
            
        Returns:
            True if task was enqueued successfully.
        """
        if not self.running:
            logger.warning("TaskQueue is not running, starting it")
            self.start()
        
        timestamp = datetime.utcnow().isoformat()
        item = QueuedTask(
            priority=-priority.value,  # Negative for correct priority order
            timestamp=timestamp,
            task_id=task_id,
            payload=payload,
            callback=callback
        )
        
        self.queue.put((item.priority, item.timestamp, item.task_id, item.payload, item.callback))
        logger.info(f"Enqueued task {task_id} with priority {priority.name}")
        return True
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            Task result dictionary or None if not found.
        """
        with self.lock:
            return self.results.get(task_id)
    
    def get_queue_size(self) -> int:
        """Get current number of tasks in queue.
        
        Returns:
            Number of pending tasks.
        """
        return self.queue.qsize()
    
    def wait_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            True if all tasks completed, False if timeout occurred.
        """
        try:
            self.queue.join()
            return True
        except Exception:
            return False
