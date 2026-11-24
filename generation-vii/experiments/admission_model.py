"""Admission checks for the finite reservation model in evolution_model.py.

Evidence is exact to a model, implementation and worker count. The controller
checks applicability and the recorded invariant result. Cryptographic trust,
real deployment and a general proof checker are outside this experiment.
"""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path

from evolution_model import State, explore


MODEL_ID = hashlib.sha256(
    Path(__file__).with_name("evolution_model.py").read_bytes().replace(b"\r\n", b"\n")
).hexdigest()
CLAIM = "accepted <= capacity and used == accepted"


@dataclass(frozen=True)
class Configuration:
    atomic: bool
    workers: int


@dataclass(frozen=True)
class Evidence:
    model_id: str
    claim: str
    configuration: Configuration
    reachable_states: int
    holds: bool


def verify(configuration):
    if configuration.workers not in (1, 2):
        raise ValueError("The finite model supports one or two workers")
    states, witness = explore(configuration.atomic, configuration.workers)
    return Evidence(MODEL_ID, CLAIM, configuration, states, witness is None)


def admit(configuration, evidence):
    if evidence.model_id != MODEL_ID or evidence.claim != CLAIM:
        return "REJECT: evidence covers a different model or claim"
    if evidence.configuration != configuration:
        return "REJECT: evidence does not cover the proposed configuration"
    if not evidence.holds:
        return "REJECT: verification found an invariant violation"
    return "ACCEPT: applicable evidence establishes the modeled invariant"


def run():
    single_split = Configuration(atomic=False, workers=1)
    combined = Configuration(atomic=False, workers=2)
    scaled_atomic = Configuration(atomic=True, workers=2)
    evidence_a = verify(single_split)
    evidence_combined = verify(combined)
    checks = [
        ("A with applicable evidence", single_split, evidence_a),
        ("A+B reusing A's evidence", combined, evidence_a),
        ("A+B after re-verification", combined, evidence_combined),
        ("B with applicable evidence", scaled_atomic, verify(scaled_atomic)),
        ("Changed implementation with A's evidence", Configuration(True, 1), evidence_a),
        ("Changed model identity", single_split, replace(evidence_a, model_id="older-model")),
        ("Changed claim", single_split, replace(evidence_a, claim="used <= capacity")),
    ]
    decisions = [
        {"case": label, "candidate": asdict(config), "evidence": asdict(evidence),
         "decision": admit(config, evidence)}
        for label, config, evidence in checks
    ]
    expected = [True, False, False, True, False, False, False]
    for row, accepted in zip(decisions, expected):
        if row["decision"].startswith("ACCEPT") != accepted:
            raise AssertionError(row)
    states, witness = explore(False, 2)
    trace = [{"event": "Initial state", **asdict(State())}]
    trace.extend({"event": event, **asdict(state)} for event, state in witness)
    return {"model_id": MODEL_ID, "claim": CLAIM, "capacity": 1,
            "combined_reachable_states": states, "trace": trace, "decisions": decisions}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
