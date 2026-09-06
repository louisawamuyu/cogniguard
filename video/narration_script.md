# CogniGuard walkthrough — narration script (Microsoft Andrew voice)

Beginner-friendly. Short sentences, plain words. The one place with `[MEASURED: ...]` gets filled in
from the real Stage 3 evaluation (evaluation/eval_stage3.py on Colab) — never guessed.

Each block below = one narrated segment paired with one slide.

---

### Segment 1 — What is CogniGuard? (title slide)
CogniGuard is a safety tool for AI agents. Think of an AI agent as a worker that reads messages,
calls tools, and takes actions on your behalf. CogniGuard's job is to keep an eye on that worker.

### Segment 2 — What it was: a flight recorder
It started as a flight recorder. Every prompt, every tool call, every file the agent touched, and
what it cost — all of it recorded, so you could replay a run later and see exactly what happened.
That's powerful for audits and debugging. But notice the limit: a flight recorder tells you what went
wrong after the plane has landed. It watches and logs. It does not step in.

### Segment 3 — The gap
Here's the problem that bugged me. Attackers don't always use the obvious words. One person writes
"ignore all previous instructions." The next writes "please disregard what you were told." Same
attack, different words. A recorder captures both, but only after the fact. I wanted CogniGuard to
catch the second one, live, before the agent acts on it.

### Segment 4 — What it is now: a real-time gate with stages
So CogniGuard grew a second job: a real-time gate that inspects a message before the agent acts.
It works in stages, cheapest check first. Stage 1 is fast pattern matching — known attack phrases and
suspicious formats, caught instantly. Most messages are settled here.

### Segment 5 — Stage 3: understanding meaning, not words
The interesting part is Stage 3, the semantic stage. Instead of matching exact words, it turns a
message into numbers that capture its meaning — an embedding. Then it compares that meaning to a
library of known attacks. "Please disregard what you were told" lands close, in meaning-space, to
"ignore all previous instructions," even though they share almost no words. If a message's meaning is
close enough to a known attack, CogniGuard flags it.

### Segment 6 — How we know it works: an honest test
A claim like that only counts if it's measured, so I built an evaluation. I wrote a set of attacks in
fresh wording the system had never seen, plus a set of ordinary, safe messages — including tricky ones
that contain words like "ignore" or "password" but are perfectly innocent. Then I measured two things:
how often it catches the rephrased attacks, and how often it wrongly flags a safe message. Both
matter — a gate that flags everything is useless.

### Segment 7 — The result
`[MEASURED: on the held-out set, Stage 3 catches __% of rephrased attacks at a __% false-positive rate.
Fill from evaluation/stage3_eval_results.json after running it on Colab. State both numbers, plainly.]`

### Segment 8 — Where this is going
This is early and honest work. The number comes from one small test set and one embedding model, and
the next step is a bigger, harder set and tuning the threshold. But the shape is real: CogniGuard has
gone from a recorder that explains the past to a gate that can act in the present — and every claim
here is something I measured, not something I asserted.
