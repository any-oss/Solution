import requests
from typing import Dict, Any

class AIClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def health(self) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def generate(self, prompt: str, max_retries: int = 2) -> Dict[str, Any]:
        for attempt in range(max_retries + 1):
            try:
                resp = self.session.post(
                    f"{self.base_url}/generate",
                    json={"prompt": prompt},
                    timeout=self.timeout
                )
                resp.raise_for_status()
                return resp.json()
            except Exception:
                if attempt == max_retries:
                    raise
