#!/bin/bash
set -euo pipefail
echo "Smoke testing AI Proxy..."
if ! curl -f http://localhost:8000/health; then
    echo "Health check failed"
    exit 1
fi
echo "Health OK"
RESP=$(curl -s -X POST http://localhost:8000/generate -d '{"prompt":"test"}')
if echo "$RESP" | grep -q "backend"; then
    echo "Smoke test passed: $RESP"
else
    echo "Smoke test failed"
    exit 1
fi
