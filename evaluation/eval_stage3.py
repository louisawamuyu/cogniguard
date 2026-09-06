"""
Honest evaluation of CogniGuard's Stage 3 (semantic) detector.

What it measures: on a HELD-OUT set of rephrased attacks + realistic benign messages, how often
the semantic engine flags an attack (recall / "catch rate") and how often it wrongly flags a benign
message (false-positive rate). We report both, because a detector that flags everything gets 100%
recall and is useless. We sweep the similarity threshold and show the trade-off, then read off the
numbers at the engine's default operating threshold (0.65).

Honesty guards:
  - Leakage check: any eval attack that appears verbatim in the engine's stored examples is dropped
    (and reported), so we never test on training data.
  - Hard-negative benign messages (containing words like ignore/forget/password) are included so the
    false-positive rate is realistic.

Run on Colab (torch/sentence-transformers need a normal CPU; this laptop's CPU lacks AVX).
    python evaluation/eval_stage3.py
"""
import json
import os
import sys

import numpy as np

# make "cogniguard" importable whether run from repo root or the evaluation/ folder
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cogniguard.semantic_engine import SemanticEngine
from evaluation.eval_data import ATTACKS, BENIGN

THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
OPERATING = 0.65


def norm(s):
    return " ".join(s.lower().split())


def best_scores(engine, texts):
    """Max cosine similarity of each text against all stored threat embeddings."""
    emb = engine.model.encode(texts, convert_to_numpy=True)
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    corpus = engine.all_threat_embeddings
    corpus = corpus / np.linalg.norm(corpus, axis=1, keepdims=True)
    sims = emb @ corpus.T                      # [n_texts, n_threats]
    return sims.max(axis=1)


def metrics(attack_scores, benign_scores, thr):
    tp = int((attack_scores >= thr).sum())
    fn = int((attack_scores < thr).sum())
    fp = int((benign_scores >= thr).sum())
    tn = int((benign_scores < thr).sum())
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    acc = (tp + tn) / (tp + fn + fp + tn)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return dict(threshold=thr, tp=tp, fn=fn, fp=fp, tn=tn, recall=recall,
                precision=precision, fpr=fpr, accuracy=acc, f1=f1)


def main():
    print("Loading semantic engine (downloads all-MiniLM-L6-v2 on first run)...")
    engine = SemanticEngine()

    # --- leakage guard ---
    stored = {norm(t) for t in engine.all_threat_texts}
    kept, leaked = [], []
    for text, cat in ATTACKS:
        (leaked if norm(text) in stored else kept).append((text, cat))
    if leaked:
        print(f"\n[leakage guard] dropped {len(leaked)} attack(s) that were verbatim in the engine:")
        for t, _ in leaked:
            print("   -", t)
    attacks = kept
    print(f"\nEval set: {len(attacks)} held-out attacks | {len(BENIGN)} benign "
          f"({sum(h for _, h in BENIGN)} hard negatives)")

    attack_texts = [t for t, _ in attacks]
    benign_texts = [t for t, _ in BENIGN]
    a_scores = best_scores(engine, attack_texts)
    b_scores = best_scores(engine, benign_texts)

    # --- threshold sweep ---
    print("\nthreshold |  recall  |  FPR   | precision | accuracy |  F1")
    print("-" * 62)
    sweep = []
    for thr in THRESHOLDS:
        m = metrics(a_scores, b_scores, thr)
        sweep.append(m)
        star = "  <- default" if abs(thr - OPERATING) < 1e-9 else ""
        print(f"   {thr:.2f}   |  {m['recall']:.3f}  | {m['fpr']:.3f} |   {m['precision']:.3f}   |"
              f"  {m['accuracy']:.3f}  | {m['f1']:.3f}{star}")

    op = metrics(a_scores, b_scores, OPERATING)
    best = max(sweep, key=lambda m: m["f1"])

    # --- per-category recall at the operating threshold (headline is prompt_injection) ---
    cats = {}
    for (text, cat), sc in zip(attacks, a_scores):
        cats.setdefault(cat, []).append(sc >= OPERATING)
    print(f"\nPer-category catch rate at threshold {OPERATING}:")
    for cat, hits in sorted(cats.items()):
        print(f"   {cat:22} {np.mean(hits):.2f}  (n={len(hits)})")

    # --- qualitative: what it missed / false-alarmed on, at operating threshold ---
    print(f"\nMissed attacks (false negatives) at {OPERATING}:")
    for (text, cat), sc in zip(attacks, a_scores):
        if sc < OPERATING:
            print(f"   [{sc:.2f}] {text}")
    print(f"\nFalse alarms on benign (false positives) at {OPERATING}:")
    for (text, hard), sc in zip(BENIGN, b_scores):
        if sc >= OPERATING:
            tag = " (hard negative)" if hard else ""
            print(f"   [{sc:.2f}] {text}{tag}")

    print("\n" + "=" * 62)
    print("HEADLINE (honest):")
    print(f"  At the default threshold {OPERATING}, Stage 3 catches "
          f"{op['recall']*100:.0f}% of held-out rephrased attacks (misses {op['fn']}/"
          f"{op['tp']+op['fn']}), with a {op['fpr']*100:.0f}% false-positive rate on benign messages.")
    print(f"  Best-F1 operating point: threshold {best['threshold']:.2f} -> "
          f"recall {best['recall']*100:.0f}%, FPR {best['fpr']*100:.0f}%, F1 {best['f1']:.2f}.")
    print("=" * 62)

    out = {
        "n_attacks": len(attacks), "n_benign": len(BENIGN),
        "n_hard_negatives": int(sum(h for _, h in BENIGN)),
        "leaked_dropped": [t for t, _ in leaked],
        "operating_threshold": OPERATING, "operating": op,
        "best_f1": best, "sweep": sweep,
        "per_category_recall_at_operating": {c: float(np.mean(v)) for c, v in cats.items()},
    }
    path = os.path.join(HERE, "stage3_eval_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
