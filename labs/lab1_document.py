"""Lab 1 - Documentation: generate a model card and a datasheet, then lint them.

Run:  python labs/lab1_document.py
Task: improve the two weakest human-written sections until the linter is quiet.
"""
import re

from common import OUT, SEED, banner  # noqa: F401  (sets sys.path to the toolkit)
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from model_card_generator import generate_model_card, save_model_card

HUMAN_SECTIONS = ["Intended Use", "Out-of-Scope Use", "Training Data",
                  "Ethical Considerations", "Limitations"]
VAGUE = ["may be biased", "use with caution", "n/a", "tbd", "none", "various", "etc"]


def lint_card(markdown: str, min_words: int = 25) -> list[str]:
    """Flag human-written sections that are too short or contain vague phrases."""
    problems = []
    for name in HUMAN_SECTIONS:
        m = re.search(rf"## {re.escape(name)}\n\n(.*?)(?=\n## |\Z)", markdown, re.S)
        text = m.group(1).strip() if m else ""
        words = len(text.split())
        if words < min_words:
            problems.append(f"{name}: only {words} words (min {min_words})")
        hits = [v for v in VAGUE if re.search(rf"\b{re.escape(v)}\b", text.lower())]
        if hits:
            problems.append(f"{name}: vague phrase(s) {hits}")
        if name in ("Training Data", "Limitations") and not re.search(r"\d", text):
            problems.append(f"{name}: no numbers - state sizes, rates or gaps")
    return problems


data = load_breast_cancer()
X_tr, X_te, y_tr, y_te = train_test_split(data.data, data.target, test_size=0.2,
                                          random_state=SEED)
model = RandomForestClassifier(n_estimators=100, random_state=SEED).fit(X_tr, y_tr)

banner("Lab 1a - a vague model card (what NOT to ship)")
vague = generate_model_card(
    model=model, model_name="Breast Cancer Classifier", model_version="0.9.0",
    X_test=X_te, y_test=y_te,
    intended_use="Cancer detection.",
    out_of_scope_use="N/A",
    training_data_description="Public dataset.",
    ethical_considerations="May be biased. Use with caution.",
    limitations="Various.",
)
for p in lint_card(vague):
    print("  FLAG", p)

banner("Lab 1b - a specific model card (edit these strings in class)")
specific = generate_model_card(
    model=model, model_name="Breast Cancer Classifier", model_version="1.0.0",
    X_test=X_te, y_test=y_te,
    intended_use=("Clinical decision support: classifies fine-needle-aspirate measurements "
                  "as malignant or benign to prioritise review. A clinician always makes the "
                  "final diagnosis; the score is advisory and logged with each case."),
    out_of_scope_use=("Not for use as the sole basis of a diagnosis, for screening populations "
                      "outside the original cohort, or with features from other imaging "
                      "pipelines without re-validation and a new model card version."),
    training_data_description=("Wisconsin Breast Cancer Dataset: 569 samples, 30 features from "
                               "digitised FNA images; 357 benign and 212 malignant. 80/20 split "
                               "with random_state=42 for the reported metrics."),
    ethical_considerations=("Data comes from a single institution, so age, ethnicity and imaging "
                            "equipment are not representative of a general population. Before "
                            "deployment, report recall per age band and per site, because a "
                            "missed malignancy is the costliest error."),
    limitations=("Uses only the 30 Wisconsin features; ignores patient history, genetics and "
                 "imaging artefacts. Performance on other institutions is unknown. Metrics come "
                 "from 114 test samples, so confidence intervals are wide."),
)
problems = lint_card(specific)
print("  no flags" if not problems else "\n".join("  FLAG " + p for p in problems))
save_model_card(specific, f"{OUT}/MODEL_CARD.md")

banner("Lab 1c - datasheet (uses the toolkit example as-is)")
import runpy, os  # noqa: E402
cwd = os.getcwd(); os.chdir(OUT)
runpy.run_path(os.path.join(os.path.dirname(OUT), "toolkit", "examples", "example_datasheet.py"))
os.chdir(cwd)
print(f"\nOutputs in {OUT}: MODEL_CARD.md, DATASHEET.md")
