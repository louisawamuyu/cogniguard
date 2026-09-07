"""
Honest evaluation of the COMBINED gate: Stage 1 (fast keyword/regex patterns) + Stage 3 (semantic).
The idea: Stage 1 catches literal attacks, Stage 3 catches rephrased ones. Flag if EITHER fires.
We measure recall AND false-positive rate for Stage 1 alone, Stage 3 alone, and Combined -- because
combining can also raise false positives (hard-negative benign messages contain trigger words).

Run on Colab (needs torch/sentence-transformers).
    python evaluation/eval_pipeline.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cogniguard.semantic_engine import SemanticEngine
from cogniguard import CogniGuardEngine
from evaluation.eval_data import ATTACKS, BENIGN
from evaluation.eval_stage3 import best_scores, norm


def stage1_flags(engine1, texts):
    out = []
    for t in texts:
        try:
            r = engine1.detect_demo(t, {}, {})
            flagged = getattr(getattr(r, "threat_level", None), "name", "SAFE") != "SAFE"
        except Exception:
            flagged = False
        out.append(bool(flagged))
    return np.array(out)


def report(name, a_flag, b_flag):
    tp = int(a_flag.sum()); fn = int((~a_flag).sum())
    fp = int(b_flag.sum()); tn = int((~b_flag).sum())
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    print(f"{name:28} recall={rec:.2f}  FPR={fpr:.2f}  precision={prec:.2f}  F1={f1:.2f}")
    return dict(recall=rec, fpr=fpr, precision=prec, f1=f1, tp=tp, fn=fn, fp=fp, tn=tn)


def main():
    s3 = SemanticEngine()
    s1 = CogniGuardEngine()

    stored = {norm(t) for t in s3.all_threat_texts}
    attacks = [(t, c) for (t, c) in ATTACKS if norm(t) not in stored]
    a_texts = [t for t, _ in attacks]
    b_texts = [t for t, _ in BENIGN]
    print(f"eval: {len(a_texts)} held-out attacks | {len(b_texts)} benign\n")

    a3 = best_scores(s3, a_texts); b3 = best_scores(s3, b_texts)
    a1 = stage1_flags(s1, a_texts); b1 = stage1_flags(s1, b_texts)

    res = {}
    res["stage1_patterns"] = report("Stage 1 (patterns only)", a1, b1)
    for thr in (0.65, 0.50):
        res[f"stage3@{thr}"] = report(f"Stage 3 (semantic) @{thr}", a3 >= thr, b3 >= thr)
    for thr in (0.65, 0.50):
        res[f"combined@{thr}"] = report(f"Combined (S1 OR S3@{thr})", a1 | (a3 >= thr), b1 | (b3 >= thr))

    json.dump(res, open(os.path.join(HERE, "pipeline_eval_results.json"), "w"), indent=2)
    print("\nsaved -> evaluation/pipeline_eval_results.json")
    print("[read] pick the row with the best recall you can accept for its false-positive rate.")


if __name__ == "__main__":
    main()
