import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
CPU_BACKEND_URL = os.getenv("CPU_BACKEND_URL", "http://localhost:8001")
GPU_BACKEND_URL = os.getenv("GPU_BACKEND_URL", "http://localhost:8002")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "10"))
HEALTH_CHECK_PATH = os.getenv("HEALTH_CHECK_PATH", "/health")
