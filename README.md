# Hands-on lab — AI Regulatory Compliance Auditing

MK1WP002 · Applied AI Systems Evaluation and Governance · Hendrik Tampubolon, Ph.D.

Builds on the companion code of R. Paul, *The AI Governance Handbook* (freeCodeCamp, 2026),
<https://github.com/RudrenduPaul/ai-governance-toolkit> (MIT licence).

## Reproducibility

| What | How it is pinned |
|---|---|
| Toolkit code | commit `743f2150` (11 Apr 2026), checked out by `setup.sh` |
| Python packages | exact versions in `requirements-lock.txt` |
| Python | 3.12 (3.10+ works) |
| Randomness | every generator, split and model uses seed 42 |
| Expected results | `EXPECTED_OUTPUT.txt` (hashes and UUIDs masked — they change per run) |

Two consecutive runs produce identical output apart from timestamps, hashes and UUIDs.

## Quick start (Linux, macOS, WSL; ~2 minutes)

```bash
bash setup.sh            # clone toolkit @ pinned commit, create .venv, install, smoke-test
source .venv/bin/activate
bash run_all.sh          # all five labs; transcript in out/run_all.log
```

Windows without WSL: run the commands inside `setup.sh` by hand, using `.venv\Scripts\activate`.

## The five labs

| Lab | File | Time | What you do |
|---|---|---|---|
| 1 Document | `labs/lab1_document.py` | 15 min | Generate a vague and a specific model card; a linter flags weak sections. Rewrite until quiet. |
| 2 Measure | `labs/lab2_bias.py` | 25 min | Audit the handbook's scenario (passes) and a proxy scenario (fails); mitigate and re-audit. |
| 3 Log | `labs/lab3_audit_trail.py` | 15 min | Tamper with the log, trigger the restart bug, apply the fix, then forge a whole chain. |
| 4 Oversee | `labs/lab4_hitl.py` | 20 min | Check calibration, sweep τ, route the test set through the review queue. |
| 5 Gate | `labs/lab5_ci_gate.py` | 10 min | Run the pytest gate on clean vs. proxy data; see the merge blocked. |

Run one lab at a time with `python labs/lab2_bias.py`, and so on.

## Deliverable (one page per group)

1. Lab 1: the two sections you rewrote, before and after.
2. Lab 2: the results table and one paragraph: which mitigation you would ship, and why, given the accuracy and equalized-odds cost.
3. Lab 3: a fix for the midnight case (the chain continues across daily files, but `verify_chain` starts each file at `genesis`).
4. Lab 4: your τ, the escalation and override rates it produces, and whether the model needs retraining.
5. Lab 5: a justified threshold for the precision gap, turning the `xfail` into a real gate.

## Notes

* The handbook says the loan-audit example will "likely" fail. Reproduced, it **passes** (DI ≈ 0.98): the simulation draws income, credit score and debt ratio independently of gender, so there is no proxy to learn. The bias shows up instead as a precision gap. Lab 2 adds a proxy (`proxy_gap=12000`) to show the failure the handbook describes.
* The handbook fits `ThresholdOptimizer` on the test set; Lab 2 fits it on training data.
* The handbook's default τ = 0.85 escalates ~58% of cases for this model; Lab 4 shows why τ must be chosen from validation data.
* Lab data is synthetic. Numbers are for teaching, not claims about real lenders.
