"""P2 independent check of "Monty-coin" (K-5).
N doors, 1 car uniform, you hold door 0. Host knows; over each goat door he opens it w.p. q
(car never). Variant A: your door may be opened too. Variant B: your door is protected.
Then you pick a closed door optimally (forced), or (walk) may leave: car +1, goat -2, leave 0.
Exact: brute force over car x subsets (small N) with Fraction; closed form via symmetry for any N.
MC: 2e5 trials.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
import random

def brute(N, q, protect, walk=False):
    q = F(q)
    obs = {}  # closed-set -> list of joint probs per door
    for car in range(N):
        goats = [d for d in range(N) if d != car and not (protect and d == 0)]
        for bits in product([0, 1], repeat=len(goats)):
            p = F(1, N)
            opened = set()
            for g, b in zip(goats, bits):
                p *= q if b else 1 - q
                if b: opened.add(g)
            key = frozenset(opened)
            v = obs.setdefault(key, [F(0)] * N)
            v[car] += p
    tot = F(0)
    for opened, v in obs.items():
        closed = [d for d in range(N) if d not in opened]
        pz = sum(v)
        best = max(v[d] for d in closed)
        if walk:
            tot += max(F(0), best - 2 * (pz - best))
        else:
            tot += best
    return tot

def closed_form(N, q, protect, walk=False):
    q = F(q); tot = F(0)
    if not protect:
        # closed doors all symmetric: C = 1 + Bin(N-1, 1-q); posterior 1/C each
        for k in range(N):
            pk = comb(N - 1, k) * (1 - q) ** k * q ** (N - 1 - k)
            post = F(1, 1 + k)
            tot += pk * (max(F(0), 3 * post - 2) if walk else post)
        return tot
    # protected: m = closed other doors; your door weight (1-q), each other closed weight 1
    for m in range(N):
        # P(m) = sum over car location
        p_yours = F(1, N) * comb(N - 1, m) * (1 - q) ** m * q ** (N - 1 - m)
        p_other = F(N - 1, N) * comb(N - 2, m - 1) * (1 - q) ** (m - 1) * q ** (N - 1 - m) if m >= 1 else F(0)
        pm = p_yours + p_other
        if m == 0:
            post = F(1)
        else:
            post = max(F(1), 1 - q) / (m + 1 - q)
        tot += pm * (max(F(0), 3 * post - 2) if walk else post)
    return tot

def mc(N, q, protect, walk=False, n=200_000, seed=1):
    rng = random.Random(seed); s = 0
    qq = float(q)
    for _ in range(n):
        car = rng.randrange(N)
        closed = [d for d in range(N) if d == car or (protect and d == 0) or rng.random() >= qq]
        if protect:
            others = [d for d in closed if d != 0]
            if not others:
                pick, post = 0, 1.0
            else:
                pick, post = others[0], 1 / (len(others) + 1 - qq)
        else:
            pick, post = closed[rng.randrange(len(closed))], 1 / len(closed)
        win = pick == car
        if walk:
            s += (1 if win else -2) if 3 * post - 2 > 0 else 0
        else:
            s += win
    return s / n

if __name__ == "__main__":
    for q in [F(1, 2), F(1, 3), F(9, 10)]:
        f = (1 + q + q * q) / 3
        a, b = brute(3, q, False), brute(3, q, True)
        print(f"N=3 q={q}: A={a} B={b} formula={f}  MC A={mc(3,q,False):.4f} B={mc(3,q,True):.4f} ({float(f):.4f})")
    for walk_q in [F(1, 2)]:
        a, b = brute(3, walk_q, False, True), brute(3, walk_q, True, True)
        print(f"N=3 walk q=1/2: A={a} B={b}  MC A={mc(3,walk_q,False,True):.4f} B={mc(3,walk_q,True,True):.4f}")
    print("closed form vs brute, N=2..8, q in {1/2,1/3,9/10}:")
    ok = all(brute(N, q, p, w) == closed_form(N, q, p, w)
             for N in range(2, 9) for q in [F(1,2), F(1,3), F(9,10)] for p in (0, 1) for w in (0, 1))
    print("  agree:", ok)
    print("N, q, forced A, forced B, walk A, walk B")
    for N in [3, 4, 10, 100]:
        for q in [F(1, 2), F(9, 10)]:
            r = [closed_form(N, q, p, w) for w in (0, 1) for p in (0, 1)]
            print(N, q, *[f"{float(x):.4f}" for x in r])
