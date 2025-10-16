!/bin/bash

set -eux

# Lint
pip install ruff typos
# Type
pip install mypy
# Test
pip install pytest coverage pytest-cov pytest-asyncio httpx numpy

if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
