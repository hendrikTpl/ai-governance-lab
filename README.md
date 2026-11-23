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

- Setup
[Setup](./docs/setup.sh.png)

- Run Experiments
[run](./docs/run_all.sh.png)

```
./run_all.sh 

================================================================
Lab 1a - a vague model card (what NOT to ship)
================================================================
  FLAG Intended Use: only 2 words (min 25)
  FLAG Out-of-Scope Use: only 1 words (min 25)
  FLAG Out-of-Scope Use: vague phrase(s) ['n/a']
  FLAG Training Data: only 2 words (min 25)
  FLAG Training Data: no numbers - state sizes, rates or gaps
  FLAG Ethical Considerations: only 6 words (min 25)
  FLAG Ethical Considerations: vague phrase(s) ['may be biased', 'use with caution']
  FLAG Limitations: only 1 words (min 25)
  FLAG Limitations: vague phrase(s) ['various']
  FLAG Limitations: no numbers - state sizes, rates or gaps

================================================================
Lab 1b - a specific model card (edit these strings in class)
================================================================
  no flags
Model card saved to /home/hendrik/Documents/supervision/POC/ai-governance-lab/out/MODEL_CARD.md

================================================================
Lab 1c - datasheet (uses the toolkit example as-is)
================================================================
Datasheet saved to DATASHEET.md

Outputs in /home/hendrik/Documents/supervision/POC/ai-governance-lab/out: MODEL_CARD.md, DATASHEET.md

================================================================
Lab 2a - audit: handbook scenario vs. proxy scenario
================================================================
scenario                             acc  DP gap  EO gap     DI  prec F prec M   gate
A  handbook (no proxy)             0.772   0.006   0.121  0.987   0.628  0.848   PASS
B  income is a proxy (gap 12k)     0.805   0.235   0.080  0.513   0.700  0.832   FAIL

================================================================
Lab 2b - mitigate scenario B, then re-audit
================================================================
scenario                             acc  DP gap  EO gap     DI  prec F prec M   gate
B  baseline                        0.805   0.235   0.080  0.513   0.700  0.832   FAIL
B  in-processing (ExpGradient)     0.762   0.121   0.051  0.704   0.586  0.844   FAIL
B  post-processing (ThresholdOpt)  0.733   0.038   0.285  0.894   0.552  0.878   PASS

Note: the handbook fits ThresholdOptimizer on the test set; here it is fitted on
training data so the re-audit is not evaluated on data the mitigator has seen.

================================================================
Lab 3a - a clean chain verifies
================================================================
Chain verified: 5 records, all hashes valid.

================================================================
Lab 3b - edit one record after the fact
================================================================
Hash mismatch at line 3: record has been tampered with

================================================================
Lab 3c - delete one record
================================================================
Chain broken at line 2: expected previous_hash 59cc0ff49e0640dc011fc82646a62b02086a609edda4e1c17d2671168283b744, got 9d034f91d1c3f86961aa72cc61ebcff1372593c3e5762dcee71eb577c526a519

================================================================
Lab 3d - the restart bug: a new process starts again at 'genesis'
================================================================
Chain broken at line 4: expected previous_hash a5440e9d7e092518e0bcd5582b0b7f64da13e088f7379a99353bce365fb17589, got genesis

================================================================
Lab 3e - fixed: PersistentAuditTrail resumes from the last hash
================================================================
Chain verified: 5 records, all hashes valid.

================================================================
Lab 3f - but an attacker who controls the file can rebuild the whole chain
================================================================
Chain verified: 5 records, all hashes valid.
-> tamper-EVIDENT only against partial edits. Anchor the head hash elsewhere
   (WORM bucket, separate service, signed checkpoint) to make rewrites detectable.

================================================================
Lab 4a - is 'confidence' a probability? (validation set)
================================================================
raw GBM                Brier 0.1377   ECE 0.0352
isotonic-calibrated    Brier 0.1364   ECE 0.0252
reliability (calibrated): 0.05->0.05  0.30->0.31  0.51->0.40  0.68->0.69  0.94->0.97

================================================================
Lab 4b - sweep tau: escalation rate vs. accuracy of auto-decisions
================================================================
  tau  escalated  auto acc
 0.60      5.8%     0.820
 0.70     35.8%     0.887
 0.75     48.3%     0.929
 0.80     54.2%     0.958
 0.85     57.9%     0.966
 0.90     61.2%     0.968
 0.95     74.0%     0.974

Chosen tau for ~15% escalation: 0.646

================================================================
Lab 4c - route the test set through HumanInTheLoop (reviewer = ground truth)
================================================================
escalation rate 15.9%   override rate 42.4%
Handbook rules of thumb: escalation 10-15%; override > 50% means retrain, not re-threshold.
..x                                                                      [100%]
=========================== short test summary info ============================
XFAIL labs/tests/test_lab_gate.py::test_precision_gap_documented - precision gap 0.220: not gated yet - write the decision in the model card
2 passed, 1 xfailed in 0.71s
FFx                                                                      [100%]
=================================== FAILURES ===================================
E   AssertionError: DI 0.513 < 0.8 - release blocked
    assert np.float64(0.5130654946734821) >= 0.8
/home/hendrik/Documents/supervision/POC/ai-governance-lab/labs/tests/test_lab_gate.py:32: AssertionError: DI 0.513 < 0.8 - release blocked
E   AssertionError: parity gap 0.235 > 0.10 - release blocked
    assert np.float64(0.2353063391661665) <= 0.1
/home/hendrik/Documents/supervision/POC/ai-governance-lab/labs/tests/test_lab_gate.py:37: AssertionError: parity gap 0.235 > 0.10 - release blocked
=========================== short test summary info ============================
XFAIL labs/tests/test_lab_gate.py::test_precision_gap_documented - precision gap 0.132: not gated yet - write the decision in the model card
2 failed, 1 xfailed in 0.73s

================================================================
Lab 5 - CI gate with PROXY_GAP=0
================================================================
-> pytest exit code 0: MERGE ALLOWED

================================================================
Lab 5 - CI gate with PROXY_GAP=12000
================================================================
-> pytest exit code 1: MERGE BLOCKED
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
