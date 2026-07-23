#!/usr/bin/env python3
"""Command-line interface for the AI Proxy service.

This module provides CLI tools for:
- Health checking
- Prompt generation
- Database analytics
- System diagnostics
"""
import argparse
import json
import sys
from typing import Any, Dict, Optional

import requests

from core.database import get_database, close_database


def make_request(
    url: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 5
) -> Dict[str, Any]:
    """Make an HTTP request and return JSON response.
    
    Args:
        url: The URL to request.
        method: HTTP method (GET or POST).
        data: Optional JSON data for POST requests.
        timeout: Request timeout in seconds.
        
    Returns:
        JSON response as a dictionary.
        
    Raises:
        requests.RequestException: If the request fails.
    """
    if method == "GET":
        resp = requests.get(url, timeout=timeout)
    elif method == "POST":
        resp = requests.post(url, json=data, timeout=timeout)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    resp.raise_for_status()
    return resp.json()


def check_health(host: str) -> int:
    """Check the health status of the service.

    Args:
        host: Base URL of the service.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        result = make_request(f"{host}/health", timeout=5)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def generate_prompt(host: str, prompt: str, verbose: bool = False) -> int:
    """Send a prompt to the service for generation.

    Args:
        host: Base URL of the service.
        prompt: The input prompt to send.
        verbose: Whether to print full JSON response.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        result = make_request(
            f"{host}/generate",
            method="POST",
            data={"prompt": prompt},
            timeout=10
        )

        if verbose:
            print(json.dumps(result, indent=2))
        else:
            backend = result.get('backend', 'unknown')
            response_text = result.get('result', result)
            print(f"Backend: {backend} | Result: {response_text}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
        
    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(description="AI Proxy CLI")
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Base URL of the AI Proxy service"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check service health status"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Send a prompt for generation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Show database analytics"
    )
    parser.add_argument(
        "--cleanup-days",
        type=int,
        default=0,
        help="Clean up database records older than N days"
    )

    args = parser.parse_args(argv)

    if args.health:
        return check_health(args.host)
    elif args.prompt:
        try:
            return generate_prompt(args.host, args.prompt, args.verbose)
        finally:
            close_database()
    elif args.analytics:
        try:
            db = get_database()
            analytics = db.get_analytics(hours=24)
            print(json.dumps(analytics, indent=2))
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            close_database()
    elif args.cleanup_days > 0:
        try:
            db = get_database()
            deleted = db.cleanup_old_data(days=args.cleanup_days)
            print(f"Cleaned up {deleted} old records")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            close_database()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
