#!/usr/bin/env python3
import argparse
import requests
import sys
import json

def main():
    parser = argparse.ArgumentParser(description="AI Proxy CLI")
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--prompt", type=str)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.health:
        try:
            r = requests.get(f"{args.host}/health", timeout=5)
            r.raise_for_status()
            print(json.dumps(r.json(), indent=2))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.prompt:
        try:
            r = requests.post(f"{args.host}/generate", json={"prompt": args.prompt}, timeout=10)
            r.raise_for_status()
            data = r.json()
            if args.verbose:
                print(json.dumps(data, indent=2))
            else:
                print(f"Backend: {data.get('backend', 'unknown')} | Result: {data.get('result', data)}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
