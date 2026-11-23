"""Lab 4 - Human-in-the-loop: choose tau from data, and check calibration first.

Run:  python labs/lab4_hitl.py
"""
import shutil

import numpy as np
from common import FEATURES, OUT, SEED, banner, make_loan_data
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split

from audit_trail import AuditTrail
from human_in_the_loop import HumanInTheLoop

df = make_loan_data(n=6000)
X, y = df[FEATURES], df["approved"]
X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.4, random_state=SEED)
X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=SEED)

raw = GradientBoostingClassifier(n_estimators=100, random_state=SEED).fit(X_tr, y_tr)
cal = CalibratedClassifierCV(GradientBoostingClassifier(n_estimators=100, random_state=SEED),
                             method="isotonic", cv=5).fit(X_tr, y_tr)


def ece(y_true, p, bins=10):
    """Expected calibration error of the predicted-class confidence."""
    conf = np.maximum(p, 1 - p); correct = ((p >= 0.5) == y_true)
    edges = np.linspace(0.5, 1.0, bins + 1); e = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        if m.any():
            e += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return e


banner("Lab 4a - is 'confidence' a probability? (validation set)")
for name, mdl in [("raw GBM", raw), ("isotonic-calibrated", cal)]:
    p = mdl.predict_proba(X_val)[:, 1]
    print(f"{name:<22} Brier {brier_score_loss(y_val, p):.4f}   ECE {ece(y_val.values, p):.4f}")
frac, mean = calibration_curve(y_val, cal.predict_proba(X_val)[:, 1], n_bins=5)
print("reliability (calibrated): " + "  ".join(f"{m:.2f}->{f:.2f}" for m, f in zip(mean, frac)))

banner("Lab 4b - sweep tau: escalation rate vs. accuracy of auto-decisions")
p = cal.predict_proba(X_val)[:, 1]
conf = np.maximum(p, 1 - p); pred = (p >= 0.5).astype(int)
print(f"{'tau':>5}{'escalated':>11}{'auto acc':>10}")
for tau in [0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
    auto = conf >= tau
    acc = (pred[auto] == y_val.values[auto]).mean() if auto.any() else float("nan")
    print(f"{tau:>5.2f}{1 - auto.mean():>10.1%}{acc:>10.3f}")

target = 0.15
tau = float(np.quantile(conf, target))
print(f"\nChosen tau for ~{target:.0%} escalation: {tau:.3f}")

banner("Lab 4c - route the test set through HumanInTheLoop (reviewer = ground truth)")
log_dir = f"{OUT}/hitl_logs"; shutil.rmtree(log_dir, ignore_errors=True)
hitl = HumanInTheLoop(confidence_threshold=tau, audit=AuditTrail(log_dir))
p_te = cal.predict_proba(X_te)[:, 1]
for i, (pi, yi) in enumerate(zip(p_te, y_te.values)):
    label = int(pi >= 0.5)
    hitl.evaluate(model_id="loan-model", model_version="2.1.0",
                  input_data={"row": int(i)}, prediction={"class": label},
                  confidence=float(max(pi, 1 - pi)))
truth = dict(enumerate(y_te.values))
for item in hitl.get_pending_reviews():
    correct = truth[item.input_data["row"]] == item.prediction["class"]
    hitl.submit_review(item.review_id, reviewer_id="ta-01",
                       decision="approved" if correct else "modified",
                       override=None if correct else {"class": 1 - item.prediction["class"]},
                       reason="matches file" if correct else "ground truth differs")
print(f"escalation rate {hitl.get_escalation_rate():.1%}   override rate {hitl.get_override_rate():.1%}")
print("Handbook rules of thumb: escalation 10-15%; override > 50% means retrain, not re-threshold.")
