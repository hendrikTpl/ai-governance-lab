#!/usr/bin/env bash
# One-command, reproducible setup for the AI governance hands-on lab.
# Usage:  bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

REPO_URL="https://github.com/RudrenduPaul/ai-governance-toolkit.git"
REPO_COMMIT="743f2150eb4ebaf61219589b8855d3d56e494c13"   # pinned: 11 Apr 2026

# 1. Companion code, pinned to one commit so every student runs the same code
if [ ! -d toolkit/.git ]; then
  git clone --quiet "$REPO_URL" toolkit
fi
git -C toolkit fetch --quiet origin "$REPO_COMMIT" || true
git -C toolkit checkout --quiet "$REPO_COMMIT"
echo "toolkit @ $(git -C toolkit rev-parse --short HEAD)"

# 2. Isolated environment with exact package versions
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements-lock.txt
python -c "import sys, sklearn, fairlearn; print('python', sys.version.split()[0], '| sklearn', sklearn.__version__, '| fairlearn', fairlearn.__version__)"

# 3. Smoke test: the toolkit's own governance suite must pass
python -m pytest -q toolkit/tests
echo "Setup OK. Activate with: source .venv/bin/activate"
