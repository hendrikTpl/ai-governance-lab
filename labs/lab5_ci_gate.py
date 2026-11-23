"""Lab 5 - Run the governance gate on clean and proxy data, as CI would.

Run:  python labs/lab5_ci_gate.py
"""
import os
import subprocess
import sys

from common import LAB_ROOT, banner

for gap in ("0", "12000"):
    banner(f"Lab 5 - CI gate with PROXY_GAP={gap}")
    env = dict(os.environ, PROXY_GAP=gap)
    code = subprocess.call([sys.executable, "-m", "pytest", "-q", "-rxX", "--tb=line",
                            os.path.join(LAB_ROOT, "labs", "tests")], env=env, cwd=LAB_ROOT)
    print(f"-> pytest exit code {code}: {'MERGE ALLOWED' if code == 0 else 'MERGE BLOCKED'}")
