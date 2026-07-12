#!/bin/bash
set -e
git revert --no-commit HEAD
git commit -m "Rollback deployment"
git push origin main
