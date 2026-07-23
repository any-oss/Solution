"""Configuration settings for the AI Proxy system."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    """Immutable configuration container."""
    host: str = "0.0.0.0"
    port: int = 8000
    cpu_backend_url: str = "http://localhost:8001"
    gpu_backend_url: str = "http://localhost:8002"
    log_level: str = "INFO"
    max_concurrency: int = 10
    health_check_path: str = "/health"

    @classmethod
    def from_env(cls, prefix: str = "") -> 'Config':
        """Create configuration from environment variables."""
        def get_env(key: str, default: str) -> str:
            return os.getenv(f"{prefix}{key}", default)

        return cls(
            host=get_env("HOST", "0.0.0.0"),
            port=int(get_env("PORT", "8000")),
            cpu_backend_url=get_env("CPU_BACKEND_URL", "http://localhost:8001"),
            gpu_backend_url=get_env("GPU_BACKEND_URL", "http://localhost:8002"),
            log_level=get_env("LOG_LEVEL", "INFO"),
            max_concurrency=int(get_env("MAX_CONCURRENCY", "10")),
            health_check_path=get_env("HEALTH_CHECK_PATH", "/health"),
        )


_default_config: Optional[Config] = None


def get_config() -> Config:
    """Get the default configuration instance."""
    global _default_config
    if _default_config is None:
        _default_config = Config.from_env()
    return _default_config


config = get_config()

HOST = config.host
PORT = config.port
CPU_BACKEND_URL = config.cpu_backend_url
GPU_BACKEND_URL = config.gpu_backend_url
LOG_LEVEL = config.log_level
MAX_CONCURRENCY = config.max_concurrency
HEALTH_CHECK_PATH = config.health_check_path
