#!/usr/bin/env python3
"""Database initialization script for AI Agent System."""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(db_path: str = "ai_agent.db") -> None:
    """Initialize the database with schema and default data.
    
    Args:
        db_path: Path to the SQLite database file.
    """
    logger.info(f"Initializing database at {db_path}...")
    
    schema_path = Path(__file__).parent / "schema.sql"
    
    if not schema_path.exists():
        logger.error(f"Schema file not found at {schema_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Verify tables were created
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"Database initialized successfully with {len(tables)} tables:")
    for table in tables:
        logger.info(f"  - {table}")
    
    conn.close()
    logger.info("Database connection closed")


if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "ai_agent.db"
    init_database(db_path)
