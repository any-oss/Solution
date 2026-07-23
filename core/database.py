"""Database module for persistent storage and analytics.

This module provides SQLite-based database operations for:
- Request logging and audit trails
- Backend performance metrics
- User session tracking
- Analytics and reporting
"""
import sqlite3
import json
import logging
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Generator
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RequestLog:
    """Represents a logged request."""
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    method: str = ""
    endpoint: str = ""
    prompt_length: int = 0
    backend: str = ""
    latency_ms: float = 0.0
    status_code: int = 200
    client_ip: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackendMetric:
    """Represents backend performance metrics."""
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    backend_type: str = "cpu"
    requests_processed: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    concurrency_level: int = 1


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    db_path: str = "ai_proxy.db"
    pool_size: int = 5
    timeout: float = 30.0
    enable_wal: bool = True
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables."""
        import os
        return cls(
            db_path=os.getenv("DB_PATH", "ai_proxy.db"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            timeout=float(os.getenv("DB_TIMEOUT", "30.0")),
            enable_wal=os.getenv("DB_ENABLE_WAL", "true").lower() == "true",
        )


class ConnectionPool:
    """Thread-safe connection pool for SQLite databases."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize the connection pool.
        
        Args:
            config: Database configuration settings.
        """
        self.config = config
        self._pool: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
        self._initialized = False
        
    def initialize(self) -> None:
        """Initialize the connection pool with pre-created connections."""
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            db_path = Path(self.config.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            for _ in range(self.config.pool_size):
                conn = sqlite3.connect(
                    str(db_path),
                    timeout=self.config.timeout,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                
                if self.config.enable_wal:
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA synchronous=NORMAL")
                    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
                    
                self._pool.append(conn)
                
            self._initialized = True
            logger.info(f"Database pool initialized with {self.config.pool_size} connections")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool.
        
        Yields:
            A SQLite connection object.
        """
        if not self._initialized:
            self.initialize()
            
        conn = None
        try:
            with self._lock:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    # Create temporary connection if pool exhausted
                    conn = sqlite3.connect(
                        self.config.db_path,
                        timeout=self.config.timeout
                    )
                    conn.row_factory = sqlite3.Row
                    
            yield conn
            
        finally:
            if conn:
                with self._lock:
                    if len(self._pool) < self.config.pool_size:
                        self._pool.append(conn)
                    else:
                        conn.close()
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()
            self._initialized = False


class Database:
    """Main database interface for AI Proxy system."""
    
    _instance: Optional['Database'] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: Optional[DatabaseConfig] = None) -> 'Database':
        """Implement singleton pattern for database instance.
        
        Args:
            config: Optional database configuration.
            
        Returns:
            Singleton database instance.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize the database.
        
        Args:
            config: Database configuration settings.
        """
        if self._initialized:
            return
            
        self.config = config or DatabaseConfig.from_env()
        self.pool = ConnectionPool(self.config)
        self._create_tables()
        self._initialized = True
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Request logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    method TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    prompt_length INTEGER DEFAULT 0,
                    backend TEXT DEFAULT '',
                    latency_ms REAL DEFAULT 0.0,
                    status_code INTEGER DEFAULT 200,
                    client_ip TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Backend metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backend_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backend_type TEXT NOT NULL,
                    requests_processed INTEGER DEFAULT 0,
                    avg_latency_ms REAL DEFAULT 0.0,
                    error_count INTEGER DEFAULT 0,
                    concurrency_level INTEGER DEFAULT 1
                )
            """)
            
            # Sessions table for user tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    client_ip TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    request_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0
                )
            """)
            
            # Routing decisions table for analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routing_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    prompt_length INTEGER NOT NULL,
                    selected_backend TEXT NOT NULL,
                    threshold_used INTEGER DEFAULT 100,
                    decision_reason TEXT DEFAULT ''
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp 
                ON request_logs(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_logs_backend 
                ON request_logs(backend)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_backend_metrics_timestamp 
                ON backend_metrics(timestamp, backend_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_last_active 
                ON sessions(last_active)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_routing_decisions_timestamp 
                ON routing_decisions(timestamp)
            """)
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    def log_request(self, request_log: RequestLog) -> int:
        """Log a request to the database.
        
        Args:
            request_log: Request log entry to store.
            
        Returns:
            The ID of the inserted row.
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO request_logs 
                (timestamp, method, endpoint, prompt_length, backend, 
                 latency_ms, status_code, client_ip, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_log.timestamp,
                request_log.method,
                request_log.endpoint,
                request_log.prompt_length,
                request_log.backend,
                request_log.latency_ms,
                request_log.status_code,
                request_log.client_ip,
                json.dumps(request_log.metadata)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def record_backend_metric(self, metric: BackendMetric) -> int:
        """Record backend performance metrics.
        
        Args:
            metric: Backend metric entry to store.
            
        Returns:
            The ID of the inserted row.
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backend_metrics 
                (timestamp, backend_type, requests_processed, 
                 avg_latency_ms, error_count, concurrency_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp,
                metric.backend_type,
                metric.requests_processed,
                metric.avg_latency_ms,
                metric.error_count,
                metric.concurrency_level
            ))
            conn.commit()
            return cursor.lastrowid
    
    def log_routing_decision(
        self, 
        prompt_length: int, 
        selected_backend: str,
        threshold: int = 100,
        reason: str = ""
    ) -> int:
        """Log a routing decision for analytics.
        
        Args:
            prompt_length: Length of the input prompt.
            selected_backend: Selected backend (cpu/gpu).
            threshold: Routing threshold used.
            reason: Reason for the routing decision.
            
        Returns:
            The ID of the inserted row.
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO routing_decisions 
                (timestamp, prompt_length, selected_backend, 
                 threshold_used, decision_reason)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now(timezone.utc).isoformat(),
                prompt_length,
                selected_backend,
                threshold,
                reason
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_or_create_session(
        self, 
        session_id: str, 
        client_ip: str
    ) -> Dict[str, Any]:
        """Get existing session or create new one.
        
        Args:
            session_id: Unique session identifier.
            client_ip: Client IP address.
            
        Returns:
            Session data as dictionary.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try to get existing session
            cursor.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            
            if row:
                # Update last active time
                cursor.execute("""
                    UPDATE sessions SET last_active = ? WHERE session_id = ?
                """, (now, session_id))
                conn.commit()
                return dict(row)
            
            # Create new session
            cursor.execute("""
                INSERT INTO sessions 
                (session_id, client_ip, created_at, last_active, 
                 request_count, total_tokens)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (session_id, client_ip, now, now))
            conn.commit()
            
            return {
                "session_id": session_id,
                "client_ip": client_ip,
                "created_at": now,
                "last_active": now,
                "request_count": 0,
                "total_tokens": 0
            }
    
    def update_session_activity(
        self, 
        session_id: str, 
        tokens_used: int = 0
    ) -> None:
        """Update session activity counters.
        
        Args:
            session_id: Session identifier.
            tokens_used: Number of tokens used in this request.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET last_active = ?, 
                    request_count = request_count + 1,
                    total_tokens = total_tokens + ?
                WHERE session_id = ?
            """, (now, tokens_used, session_id))
            conn.commit()
    
    def get_analytics(
        self, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get analytics data for the specified time period.
        
        Args:
            hours: Number of hours to include in analytics.
            
        Returns:
            Analytics data including request counts, latency stats, 
            routing distribution, and error rates.
        """
        cutoff = (datetime.now(timezone.utc).timestamp() - hours * 3600)
        cutoff_str = datetime.fromtimestamp(cutoff).isoformat()
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total requests
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN backend = 'cpu' THEN 1 ELSE 0 END) as cpu_count,
                       SUM(CASE WHEN backend = 'gpu' THEN 1 ELSE 0 END) as gpu_count
                FROM request_logs
                WHERE timestamp >= ?
            """, (cutoff_str,))
            row = cursor.fetchone()
            request_stats = dict(row) if row else {}
            
            # Average latency by backend
            cursor.execute("""
                SELECT backend, AVG(latency_ms) as avg_latency,
                       MAX(latency_ms) as max_latency,
                       MIN(latency_ms) as min_latency
                FROM request_logs
                WHERE timestamp >= ? AND latency_ms > 0
                GROUP BY backend
            """, (cutoff_str,))
            latency_stats = {r['backend']: dict(r) for r in cursor.fetchall()}
            
            # Error rate
            cursor.execute("""
                SELECT COUNT(*) as errors,
                       (SELECT COUNT(*) FROM request_logs WHERE timestamp >= ?) as total
                FROM request_logs
                WHERE timestamp >= ? AND status_code >= 400
            """, (cutoff_str, cutoff_str))
            row = cursor.fetchone()
            error_data = dict(row) if row else {}
            error_rate = (error_data.get('errors', 0) / max(error_data.get('total', 1), 1)) * 100
            
            # Active sessions
            cursor.execute("""
                SELECT COUNT(*) as active_sessions
                FROM sessions
                WHERE last_active >= ?
            """, (cutoff_str,))
            row = cursor.fetchone()
            session_count = dict(row) if row else {}
            
            return {
                "period_hours": hours,
                "total_requests": request_stats.get('total', 0),
                "cpu_requests": request_stats.get('cpu_count', 0),
                "gpu_requests": request_stats.get('gpu_count', 0),
                "latency_by_backend": latency_stats,
                "error_count": error_data.get('errors', 0),
                "error_rate_percent": round(error_rate, 2),
                "active_sessions": session_count.get('active_sessions', 0)
            }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request logs.
        
        Args:
            limit: Maximum number of requests to return.
            
        Returns:
            List of recent request logs.
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM request_logs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days: int = 7) -> int:
        """Clean up old data from the database.
        
        Args:
            days: Number of days to retain.
            
        Returns:
            Number of rows deleted.
        """
        cutoff = (datetime.now(timezone.utc).timestamp() - days * 86400)
        cutoff_str = datetime.fromtimestamp(cutoff).isoformat()
        
        deleted = 0
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM request_logs WHERE timestamp < ?
            """, (cutoff_str,))
            deleted += cursor.rowcount
            
            cursor.execute("""
                DELETE FROM backend_metrics WHERE timestamp < ?
            """, (cutoff_str,))
            deleted += cursor.rowcount
            
            cursor.execute("""
                DELETE FROM routing_decisions WHERE timestamp < ?
            """, (cutoff_str,))
            deleted += cursor.rowcount
            
            conn.commit()
            
        logger.info(f"Cleaned up {deleted} old database records")
        return deleted
    
    def close(self) -> None:
        """Close all database connections."""
        self.pool.close_all()
        logger.info("Database connections closed")


# Global database instance
_db_instance: Optional[Database] = None


def get_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Get or create the global database instance.
    
    Args:
        config: Optional database configuration.
        
    Returns:
        Global database instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(config)
    return _db_instance


def init_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Initialize the database system.
    
    Args:
        config: Optional database configuration.
        
    Returns:
        Initialized database instance.
    """
    return get_database(config)


def close_database() -> None:
    """Close the global database connection."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None


def log_routing_decision(
    prompt_length: int,
    selected_backend: str,
    threshold: int = 100,
    reason: str = ""
) -> int:
    """Convenience function to log a routing decision.
    
    Args:
        prompt_length: Length of the input prompt.
        selected_backend: Selected backend (cpu/gpu).
        threshold: Routing threshold used.
        reason: Reason for the routing decision.
        
    Returns:
        The ID of the inserted row.
    """
    db = get_database()
    return db.log_routing_decision(prompt_length, selected_backend, threshold, reason)
