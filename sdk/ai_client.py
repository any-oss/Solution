"""AI client SDK for interacting with the AI Proxy service."""
import requests
from typing import Dict, Any, Optional


class AIClientError(Exception):
    """Base exception for AIClient errors."""
    pass


class AIClientTimeoutError(AIClientError):
    """Raised when a request times out."""
    pass


class AIClientHTTPError(AIClientError):
    """Raised when an HTTP error occurs."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class AIClient:
    """Client for interacting with the AI Proxy service.

    Attributes:
        base_url: Base URL of the AI Proxy service.
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        """Initialize the AI client.

        Args:
            base_url: Base URL of the AI Proxy service.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def health(self) -> Dict[str, Any]:
        """Check the health status of the service.

        Returns:
            Health status response as a dictionary.

        Raises:
            AIClientHTTPError: If the health check fails.
            AIClientTimeoutError: If the request times out.
        """
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout as e:
            raise AIClientTimeoutError("Health check timed out") from e
        except requests.exceptions.HTTPError as e:
            raise AIClientHTTPError(e.response.status_code, str(e)) from e

    def generate(
        self,
        prompt: str,
        max_retries: int = 2,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """Generate a response for the given prompt.

        Args:
            prompt: The input prompt to send to the service.
            max_retries: Maximum number of retry attempts on failure.
            retry_delay: Delay between retries in seconds.

        Returns:
            Generated response as a dictionary.

        Raises:
            AIClientHTTPError: If all retry attempts fail.
            AIClientTimeoutError: If the request times out.
        """
        import time as time_module

        last_exception: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                resp = self.session.post(
                    f"{self.base_url}/generate",
                    json={"prompt": prompt},
                    timeout=self.timeout
                )
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.Timeout as e:
                last_exception = AIClientTimeoutError(f"Request timed out (attempt {attempt + 1})")
            except requests.exceptions.HTTPError as e:
                last_exception = AIClientHTTPError(e.response.status_code, str(e))
            except Exception as e:
                last_exception = AIClientError(f"Request failed (attempt {attempt + 1}): {e}")

            if attempt < max_retries:
                time_module.sleep(retry_delay)

        if last_exception:
            raise last_exception
        raise AIClientError("Unknown error occurred")
