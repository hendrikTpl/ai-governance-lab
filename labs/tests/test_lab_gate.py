"""Lab 5 - governance gate. PROXY_GAP selects the training data the gate audits.

    PROXY_GAP=0     pytest labs/tests -q   -> passes (handbook-style data)
    PROXY_GAP=12000 pytest labs/tests -q   -> fails  (income is a proxy for gender)
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import FEATURES, SEED, make_loan_data  # noqa: E402
from sklearn.ensemble import GradientBoostingClassifier  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from bias_detection import run_bias_audit  # noqa: E402

PROXY_GAP = float(os.environ.get("PROXY_GAP", "0"))


@pytest.fixture(scope="module")
def audit():
    df = make_loan_data(proxy_gap=PROXY_GAP)
    X_tr, X_te, y_tr, y_te, _, s_te = train_test_split(
        df[FEATURES], df["approved"], df["gender"], test_size=0.3,
        random_state=SEED, stratify=df["gender"])
    model = GradientBoostingClassifier(n_estimators=100, random_state=SEED).fit(X_tr, y_tr)
    return run_bias_audit(y_te.values, model.predict(X_te), s_te)


def test_four_fifths_rule(audit):
    assert audit["disparate_impact_ratio"] >= 0.8, (
        f"DI {audit['disparate_impact_ratio']:.3f} < 0.8 - release blocked")


def test_parity_gap(audit):
    assert audit["demographic_parity_diff"] <= 0.10, (
        f"parity gap {audit['demographic_parity_diff']:.3f} > 0.10 - release blocked")


def test_precision_gap_documented(audit):
    """Stretch task: decide a threshold for the precision gap and justify it."""
    g = audit["metric_frame"].by_group["precision"]
    gap = abs(g["male"] - g["female"])
    if gap > 0.10:
        pytest.xfail(f"precision gap {gap:.3f}: not gated yet - write the decision in the model card")
