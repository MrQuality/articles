# Reproduce the Generation VII experiments

## 1. Resource admission with unsigned 64-bit arithmetic

The reference uses a 65-bit sum. The model checks whether either 64-bit predicate can disagree with that reference.

```sh
z3 -version
z3 admission.smt2
```

The article reports results for Z3 4.13.3. The checks should return `sat` for the wrapping predicate, `sat` for the article's concrete witness, and `unsat` for the guarded predicate. The [SMT-LIB file](admission.smt2) reconstructs the checks described in the article and includes a query for the reported witness.

## 2. Combining two scheduler changes

Run with Python 3.10 or later. The script uses only the standard library.

```sh
python evolution_model.py
```

Compare the output with [the recorded run](evolution-results.txt). The model exhaustively explores two unit requests and one unit of capacity. Only the configuration that combines a split read/write operation with two workers violates the invariant.
