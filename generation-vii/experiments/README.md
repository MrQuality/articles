# Reproduce the Generation VII experiments

## 1. Resource admission with unsigned 64-bit arithmetic

The reference uses a 65-bit sum. The model checks whether either 64-bit predicate can disagree with that reference.

```sh
z3 -version
z3 admission.smt2
```

The [recorded Z3 4.13.3 run](admission-results.txt) returns `sat` for the wrapping predicate, `sat` for the article's concrete witness, and `unsat` for the guarded predicate. It was reproduced on Windows x86-64 on 24 November 2026 using the PyPI package `z3-solver==4.13.3.0`. The [SMT-LIB file](admission.smt2) reconstructs the checks described in the article and includes a query for the reported witness.

## 2. Combining two scheduler changes

Run with Python 3.10 or later. The script uses only the standard library.

```sh
python evolution_model.py
```

Compare the output with [the recorded run](evolution-results.txt). The model exhaustively explores two unit requests and one unit of capacity. Only the configuration that combines a split read/write operation with two workers violates the invariant.

## 3. Admission based on applicable evidence

Run from this directory with Python 3.10 or later.

```sh
python admission_model.py
```

The [admission model](admission_model.py) imports the original state explorer. Compare its JSON output with [the recorded decisions and counterexample](admission-results.json). It checks the model identity, invariant, implementation and worker count before accepting evidence. The single-worker split operation and the two-worker atomic operation are accepted. Reuse of single-worker evidence for the combined configuration is rejected. Exhaustive re-verification also rejects the combined configuration.

The script checks all seven expected decisions and fails if any differ. The additional cases cover a changed implementation, model identity and claim. Evidence records are produced by the local verifier and passed directly to the admission function. The model does not authenticate external evidence or perform deployment.

## Animations and static alternatives

- [Reservation counterexample](reservation-trace.html) replays the four events in the recorded witness.
- [Evidence applicability](assurance-graph.html) steps through acceptance, scope mismatch and rejection after re-verification.

Both pages embed the JSON produced by `admission_model.py`. Playback begins on request, stops at the final state and supports manual steps. Reduced-motion preferences disable animated transitions. Each page includes a complete static table, available without JavaScript.

After changing the model, regenerate the data and both pages from this directory.

```sh
python admission_model.py > admission-results.json
python render_animations.py
```

Use a shell that redirects output as UTF-8. In Windows PowerShell 5, use `python admission_model.py | Set-Content -Encoding utf8 admission-results.json`.
