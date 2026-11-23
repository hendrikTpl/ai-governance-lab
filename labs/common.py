"""Shared helpers for the hands-on lab: path setup and a seeded data generator."""
import os
import sys

import numpy as np
import pandas as pd

LAB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLKIT = os.path.join(LAB_ROOT, "toolkit")
OUT = os.path.join(LAB_ROOT, "out")
os.makedirs(OUT, exist_ok=True)
if TOOLKIT not in sys.path:
    sys.path.insert(0, TOOLKIT)

SEED = 42
FEATURES = ["income", "credit_score", "debt_ratio"]


def make_loan_data(n: int = 2000, proxy_gap: float = 0.0, seed: int = SEED) -> pd.DataFrame:
    """Synthetic loan data, following the handbook's simulation.

    proxy_gap = 0     -> the handbook's version: features are independent of gender.
    proxy_gap = 12000 -> women's mean income is 12,000 lower, so income becomes a
                         proxy for gender (closer to real labour-market data).
    Historical labels carry a 0.1 approval penalty for women in both cases.
    """
    rng = np.random.default_rng(seed)
    gender = rng.choice(["male", "female"], n, p=[0.6, 0.4])
    female = (gender == "female").astype(float)
    income = rng.normal(55000, 15000, n) - proxy_gap * female
    credit = rng.normal(680, 50, n)
    debt = rng.uniform(0.1, 0.6, n)
    p = (0.3 + 0.3 * (income > 50000) + 0.2 * (credit > 700)
         - 0.15 * (debt > 0.4) - 0.1 * female)
    approved = (p + rng.normal(0, 0.15, n) > 0.5).astype(int)
    return pd.DataFrame({"income": income, "credit_score": credit, "debt_ratio": debt,
                         "gender": gender, "approved": approved})


def banner(title: str) -> None:
    print("\n" + "=" * 64 + f"\n{title}\n" + "=" * 64)
