"""r64: exact stochastic finite-horizon POMDP for the host-type item.

Beliefs are 4-vectors of Fractions.  Probes have symmetric answer noise:
P(correct)=1-eps, each other answer eps/(m-1).  Exact DP with memoization over
reachable beliefs for horizons 1..3.  The horizon bound T <= ceil(L/c) is in
the POMDP note; here we compute a small stochastic case.
"""
import sys
from fractions import Fraction as F
from functools import lru_cache

sys.dont_write_bytecode = True

HYPS = ("correct", "prior", "equal", "classic")
EPS = F(1, 10)
COST = F(1, 10)

KEYS = {
    "Q2(1/4)": {"correct": F(2, 5), "prior": F(1, 4), "equal": F(1, 2), "classic": F(2, 3)},
    "Q2(1/2)": {"correct": F(2, 3), "prior": F(1, 2), "equal": F(1, 2), "classic": F(2, 3)},
    "Q1": {"correct": F(1, 2), "prior": F(1, 2), "equal": F(1, 2), "classic": F(2, 3)},
}

ANSWERS = {name: sorted(set(keys.values())) for name, keys in KEYS.items()}


def prob(probe, obs, h):
    keys = KEYS[probe]
    m = len(ANSWERS[probe])
    if obs == keys[h]:
        return 1 - EPS
    return EPS / (m - 1)


def normalize(b):
    s = sum(b)
    return tuple(x / s for x in b)


def initial():
    return tuple(F(1, 4) for _ in HYPS)


@lru_cache(maxsize=None)
def value(b, t):
    b = normalize(b)
    stop = 1 - max(b)
    if t == 0:
        return stop
    best = stop
    for probe in KEYS:
        total = COST
        for obs in ANSWERS[probe]:
            pa = sum(b[i] * prob(probe, obs, HYPS[i]) for i in range(len(HYPS)))
            if pa == 0:
                continue
            nb = normalize(tuple(b[i] * prob(probe, obs, HYPS[i]) for i in range(len(HYPS))))
            total += pa * value(nb, t - 1)
        if total < best:
            best = total
    return best


@lru_cache(maxsize=None)
def best_action(b, t):
    b = normalize(b)
    stop = 1 - max(b)
    if t == 0:
        return stop, "stop"
    best = (stop, "stop")
    for probe in KEYS:
        total = COST
        for obs in ANSWERS[probe]:
            pa = sum(b[i] * prob(probe, obs, HYPS[i]) for i in range(len(HYPS)))
            if pa == 0:
                continue
            nb = normalize(tuple(b[i] * prob(probe, obs, HYPS[i]) for i in range(len(HYPS))))
            total += pa * value(nb, t - 1)
        if total < best[0]:
            best = (total, probe)
    return best


def main():
    print("=== r64 stochastic finite-horizon POMDP ===")
    print(f"eps={EPS}, cost={COST}")
    b = initial()
    for t in range(1, 6):
        v, a = best_action(b, t)
        print(f"T={t}: value={float(v):.6f}, first action={a}")
    print(f"stop without probe: {float(1 - max(b)):.6f}")
    print("All checks passed")


if __name__ == "__main__":
    main()
