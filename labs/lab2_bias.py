"""Lab 2 - Bias audit and mitigation, with and without a proxy variable.

Run:  python labs/lab2_bias.py
Question: why does the handbook's scenario PASS the four-fifths test even though
the labels are biased, and what changes when income becomes a proxy for gender?
"""
import warnings

from common import FEATURES, SEED, banner, make_loan_data
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.reductions import DemographicParity, ExponentiatedGradient
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from bias_detection import run_bias_audit

warnings.filterwarnings("ignore")


def split(df):
    return train_test_split(df[FEATURES], df["approved"], df["gender"],
                            test_size=0.3, random_state=SEED, stratify=df["gender"])


def row(name, y_true, y_pred, sens):
    r = run_bias_audit(y_true=y_true.values, y_pred=y_pred, sensitive_features=sens)
    g = r["metric_frame"].by_group
    print(f"{name:<34}{accuracy_score(y_true, y_pred):>6.3f}{r['demographic_parity_diff']:>8.3f}"
          f"{r['equalized_odds_diff']:>8.3f}{r['disparate_impact_ratio']:>7.3f}"
          f"{g.loc['female', 'precision']:>8.3f}{g.loc['male', 'precision']:>7.3f}"
          f"   {'PASS' if r['passed'] else 'FAIL'}")
    return r


header = f"{'scenario':<34}{'acc':>6}{'DP gap':>8}{'EO gap':>8}{'DI':>7}{'prec F':>8}{'prec M':>7}   gate"

banner("Lab 2a - audit: handbook scenario vs. proxy scenario")
print(header)
models = {}
for name, gap in [("A  handbook (no proxy)", 0), ("B  income is a proxy (gap 12k)", 12000)]:
    X_tr, X_te, y_tr, y_te, s_tr, s_te = split(make_loan_data(proxy_gap=gap))
    m = GradientBoostingClassifier(n_estimators=100, random_state=SEED).fit(X_tr, y_tr)
    row(name, y_te, m.predict(X_te), s_te)
    models[name] = (m, X_tr, X_te, y_tr, y_te, s_tr, s_te)

banner("Lab 2b - mitigate scenario B, then re-audit")
print(header)
m, X_tr, X_te, y_tr, y_te, s_tr, s_te = models["B  income is a proxy (gap 12k)"]
row("B  baseline", y_te, m.predict(X_te), s_te)

eg = ExponentiatedGradient(GradientBoostingClassifier(n_estimators=100, random_state=SEED),
                           constraints=DemographicParity())
eg.fit(X_tr, y_tr, sensitive_features=s_tr)
row("B  in-processing (ExpGradient)", y_te, eg.predict(X_te, random_state=SEED), s_te)

to = ThresholdOptimizer(estimator=m, constraints="demographic_parity", prefit=True,
                        predict_method="predict_proba")
to.fit(X_tr, y_tr, sensitive_features=s_tr)   # fit on TRAIN, evaluate on TEST
row("B  post-processing (ThresholdOpt)", y_te,
    to.predict(X_te, sensitive_features=s_te, random_state=SEED), s_te)

print("\nNote: the handbook fits ThresholdOptimizer on the test set; here it is fitted on")
print("training data so the re-audit is not evaluated on data the mitigator has seen.")
