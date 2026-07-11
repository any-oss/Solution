#!/bin/bash
set -e
echo "Starting rollback..."
git revert --no-commit HEAD
git commit -m "Rollback deployment"
git push origin main
echo "Rollback complete"
