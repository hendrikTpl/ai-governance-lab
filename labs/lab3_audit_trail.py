"""Lab 3 - Audit trail: tamper detection, the restart bug, and a fix.

Run:  python labs/lab3_audit_trail.py
"""
import json
import shutil
from pathlib import Path

from common import OUT, banner

from audit_trail import AuditTrail, verify_chain

LOG_DIR = Path(OUT) / "audit_logs"


def fresh():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def log_n(trail, n, start=0):
    for i in range(start, start + n):
        trail.log_prediction(model_id="loan-model", model_version="2.1.0",
                             input_data={"applicant": f"APP-{i:04d}", "income": 50000 + 1000 * i},
                             output={"class": "approved"}, confidence=0.9, user_id=f"u{i}")


def today_file():
    return next(LOG_DIR.glob("audit_*.jsonl"))


class PersistentAuditTrail(AuditTrail):
    """Fix: resume the chain from the last record on disk instead of 'genesis'."""

    def __init__(self, log_dir: str = "audit_logs"):
        super().__init__(log_dir)
        path = self._get_log_path()
        if path.exists() and path.stat().st_size > 0:
            last = path.read_text().strip().splitlines()[-1]
            self.previous_hash = json.loads(last)["hash"]


banner("Lab 3a - a clean chain verifies")
fresh(); trail = AuditTrail(str(LOG_DIR)); log_n(trail, 5)
verify_chain(str(today_file()))

banner("Lab 3b - edit one record after the fact")
lines = today_file().read_text().splitlines()
rec = json.loads(lines[2]); rec["output"]["class"] = "denied"   # quietly flip a decision
lines[2] = json.dumps(rec, sort_keys=True)
today_file().write_text("\n".join(lines) + "\n")
verify_chain(str(today_file()))

banner("Lab 3c - delete one record")
fresh(); trail = AuditTrail(str(LOG_DIR)); log_n(trail, 5)
lines = today_file().read_text().splitlines(); del lines[1]
today_file().write_text("\n".join(lines) + "\n")
verify_chain(str(today_file()))

banner("Lab 3d - the restart bug: a new process starts again at 'genesis'")
fresh()
log_n(AuditTrail(str(LOG_DIR)), 3)            # process 1
log_n(AuditTrail(str(LOG_DIR)), 2, start=3)   # process 2, same day, after a restart
verify_chain(str(today_file()))

banner("Lab 3e - fixed: PersistentAuditTrail resumes from the last hash")
fresh()
log_n(PersistentAuditTrail(str(LOG_DIR)), 3)
log_n(PersistentAuditTrail(str(LOG_DIR)), 2, start=3)
verify_chain(str(today_file()))

banner("Lab 3f - but an attacker who controls the file can rebuild the whole chain")
fresh(); log_n(AuditTrail(str(LOG_DIR)), 5)
records = [json.loads(l) for l in today_file().read_text().splitlines()]
records[2]["output"]["class"] = "denied"
forged = AuditTrail(str(LOG_DIR) + "_forged")
with open(today_file(), "w") as f:
    for r in records:
        r.pop("hash"); r.pop("previous_hash")
        h = forged._compute_hash(r)
        r["hash"], r["previous_hash"] = h, forged.previous_hash
        forged.previous_hash = h
        f.write(json.dumps(r, sort_keys=True) + "\n")
verify_chain(str(today_file()))
print("-> tamper-EVIDENT only against partial edits. Anchor the head hash elsewhere")
print("   (WORM bucket, separate service, signed checkpoint) to make rewrites detectable.")
shutil.rmtree(str(LOG_DIR) + "_forged", ignore_errors=True)
