# Pipeline Python Environment Fix

## Issue
Python 3.12+ enforces PEP 668 which prevents installing packages system-wide:
```
× This environment is externally managed
```

## Solution
Create and use a virtual environment in each pipeline stage:

```yaml
- bash: |
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -r requirements.txt
  displayName: '📦 Install dependencies'

- bash: |
    source .venv/bin/activate
    python -m scripts.deploy_agent ...
  displayName: '🚀 Deploy'
```

## Changes Applied

All stages now:
1. Create `.venv` virtual environment
2. Activate it with `source .venv/bin/activate`
3. Install packages with `pip` (not `python3 -m pip`)
4. Run scripts with `python` (not `python3`)

This ensures packages are isolated per pipeline run and don't conflict with system Python.
