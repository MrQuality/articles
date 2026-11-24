"""Exhaustive finite-state exploration of two unit reservations, capacity 1.
This is a deliberately abstract model, not verification of a deployed scheduler.
State: persisted usage, accepted count, and per-request phases.
Phase 0=not started, 1=observed available (pending write), 2=done.
The single-worker environment serializes a complete request. Atomic mode
models an indivisible check+increment. Split mode models a stale write.
"""
from collections import deque
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    used: int = 0
    accepted: int = 0
    phases: tuple[int,int] = (0,0)

def next_states(s, atomic, workers):
    for i, phase in enumerate(s.phases):
        if phase == 2:
            continue
        if workers == 1 and phase == 0 and 1 in s.phases:
            continue
        phases = list(s.phases)
        used, accepted = s.used, s.accepted
        if phase == 1:
            # The earlier read found zero; a stale write stores one.
            used = 1
            accepted += 1
            phases[i] = 2
            event = f'R{i+1}: commit prior acceptance'
        elif used == 1:
            phases[i] = 2
            event = f'R{i+1}: reject (full)'
        elif atomic:
            used, accepted = 1, accepted+1
            phases[i] = 2
            event = f'R{i+1}: atomic check + reserve'
        else:
            phases[i] = 1
            event = f'R{i+1}: observe available capacity'
        yield event, State(used, accepted, tuple(phases))

def explore(atomic, workers):
    start = State()
    q = deque([(start, [])])
    seen = {start}
    witness = None
    while q:
        s, path = q.popleft()
        if (s.accepted > 1 or s.used != s.accepted) and witness is None:
            witness = path
        for event, nxt in next_states(s, atomic, workers):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, path + [(event,nxt)]))
    return len(seen), witness

cases = [('Baseline', True, 1), ('A: software change', False, 1),
         ('B: infrastructure change', True, 2), ('A+B: combined changes', False, 2)]
if __name__ == '__main__':
    for label, atomic, workers in cases:
        states, witness = explore(atomic, workers)
        print(f'{label}: {"VIOLATION" if witness else "NO VIOLATION"}; {states} reachable states')
        if witness:
            for event, s in witness:
                print(f'  {event}; used={s.used}, accepted={s.accepted}, phases={s.phases}')
    assert all(explore(a,w)[1] is None for _,a,w in cases[:3])
    assert explore(False,2)[1] is not None
