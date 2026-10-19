"""r49: exact key for the protocol-type diagnostic item.

Game: N doors, prize uniform, subject chose A.  Before the game the host is
"informed" (K) with probability alpha, otherwise "uninformed" (R).

K: knows the prize.  Always opens B if B is empty; if the prize is behind B,
   opens C (C is then empty because A was chosen).
R: does not know.  Opens one of the N-1 unchosen doors uniformly, even if the
   prize is behind it.

Observation E: the host opened B and B is empty.

Questions:
  Q1: P(prize behind C | E)
  Q2: P(host was informed | E)
  Q3: buy a ticket paying 1 iff K, at price t?  (correct iff Q2 > t)

Q1 is 1/(N-1) for every alpha; the observation is uninformative about the
prize under this protocol.  Q2 moves from alpha to
    (N-1)*alpha / (1 + (N-2)*alpha).
A protocol-blind subject who averages the two host types' answers reports
alpha.  A subject who pattern-matches the classical Monty problem may report
2/3 for Q1 when N=3, which is wrong here.

Everything is checked by exact enumeration of (prize, host type, host action)
and by the closed formulas.  No randomness, no floating point in the checks.
"""
from fractions import Fraction as F
from itertools import product

DOORS = "ABCDE"


def host_action(N, prize, kind, action):
    """Return True iff this (prize, kind, action) is possible."""
    chosen = 0  # A
    doors = list(range(N))
    if kind == "K":
        if prize != 1:  # B is empty
            return action == 1
        # prize is B; C is empty
        return action == 2
    # R: uniform over unchosen doors, independent of prize
    return action in [d for d in doors if d != chosen]


def exact(N, alpha):
    """Enumerate all (prize, kind, action) with the stated probabilities."""
    pK = alpha
    pR = 1 - alpha
    mass = {}  # (prize, kind, action) -> probability
    for prize in range(N):
        for kind, pk in (("K", pK), ("R", pR)):
            acts = [a for a in range(N) if a != 0 and host_action(N, prize, kind, a)]
            if not acts:
                continue
            for a in acts:
                # K is deterministic; R is uniform over the N-1 unchosen doors
                pa = F(1, N - 1) if kind == "R" else F(1)
                mass[(prize, kind, a)] = pk * F(1, N) * pa
    E = {k: v for k, v in mass.items() if k[2] == 1 and k[0] != 1}
    pE = sum(E.values(), F(0))
    # conditional on E
    q1 = sum(v for (prize, kind, a), v in E.items() if prize == 2) / pE
    q2 = sum(v for (prize, kind, a), v in E.items() if kind == "K") / pE
    pEK = sum(v for (prize, kind, a), v in mass.items()
              if kind == "K" and a == 1 and prize != 1)
    pER = sum(v for (prize, kind, a), v in mass.items()
              if kind == "R" and a == 1 and prize != 1)
    return {
        "P(E|K)": pEK / pK if pK else None,
        "P(E|R)": pER / pR if pR else None,
        "P(E)": pE,
        "Q1": q1,
        "Q2": q2,
        "naive_Q2": alpha,
        "classic_Q1": F(2, 3),
    }


def closed(N, alpha):
    a = F(alpha)
    pEK = F(N - 1, N)
    pER = F(1, N)
    q1 = F(1, N - 1)
    q2 = (N - 1) * a / (1 + (N - 2) * a)
    return pEK, pER, q1, q2


def max_gap(N):
    """Max over alpha of Q2(alpha)-alpha for integer alpha grid 0..1 / 10000."""
    best = (F(-1), None)
    for i in range(1, 10000):
        a = F(i, 10000)
        gap = closed(N, a)[3] - a
        if gap > best[0]:
            best = (gap, a)
    return best


def fmt(x):
    if x is None:
        return "None"
    if isinstance(x, F):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    return str(x)


def main():
    checks = 0
    print("=== Exact enumeration vs closed formulas ===")
    for N in range(3, 7):
        for i in range(0, 21):
            alpha = F(i, 20)
            e = exact(N, alpha)
            pEK, pER, q1, q2 = closed(N, alpha)
            if alpha > 0:
                assert e["P(E|K)"] == pEK, (N, alpha, e["P(E|K)"], pEK)
                checks += 1
            if alpha < 1:
                assert e["P(E|R)"] == pER, (N, alpha, e["P(E|R)"], pER)
                checks += 1
            assert e["Q1"] == q1, (N, alpha, e["Q1"], q1)
            assert e["Q2"] == q2, (N, alpha, e["Q2"], q2)
            checks += 2
    print(f"{checks} exact equalities passed for N=3..6, alpha=0,1/20,...,1")
    print("Q1 is independent of alpha and equals 1/(N-1).")
    print("The observation changes the prize prior from 1/N to 1/(N-1).")
    print()

    print("=== Main table, N=3 ===")
    print(f"{'alpha':>6} {'Q1':>6} {'Q2 correct':>11} {'Q2 naive':>9} {'gap':>8} "
          f"{'Q3 t=3/5':>10} {'naive action':>13}")
    for alpha in [F(1, 3), F(2, 5), F(3, 7), F(1, 2), F(11, 20), F(3, 5), F(2, 3)]:
        e = exact(3, alpha)
        q2 = e["Q2"]
        gap = q2 - alpha
        buy = "buy" if q2 > F(3, 5) else ("indiff" if q2 == F(3, 5) else "refuse")
        nb = "buy" if alpha > F(3, 5) else ("indiff" if alpha == F(3, 5) else "refuse")
        print(f"{fmt(alpha):>6} {fmt(e['Q1']):>6} {fmt(q2):>11} {fmt(alpha):>9} "
              f"{fmt(gap):>8} {buy:>10} {nb:>13}")
    print()

    print("=== The three predicted profiles, N=3, alpha=1/3 ===")
    e = exact(3, F(1, 3))
    print(f"protocol-aware: Q1={fmt(e['Q1'])}, Q2={fmt(e['Q2'])}")
    print(f"protocol-blind: Q1={fmt(e['Q1'])}, Q2={fmt(e['naive_Q2'])}")
    print(f"classic-pattern: Q1={fmt(e['classic_Q1'])}, Q2=2/3 (or alpha, unspecified)")
    print("The three profiles have distinct (Q1,Q2) pairs at alpha=1/3:")
    print("  correct (1/2,1/2), blind (1/2,1/3), pattern (2/3,2/3).")
    print()

    print("=== Maximum gap of Q2 from the naive prior ===")
    for N in range(3, 11):
        gap, a = max_gap(N)
        print(f"N={N:2d}: max gap={fmt(gap):>7} at alpha={fmt(a):>8} "
              f"(posterior={fmt(F((N - 1) * a) / (1 + (N - 2) * a))})")
    print()

    print("=== Price threshold alpha* for Q3, N=3, t=3/5 ===")
    # (2a)/(1+a) > 3/5  <=>  10a > 3+3a  <=>  a > 3/7
    a_star = F(3, 7)
    assert closed(3, a_star)[3] == F(3, 5)
    print(f"correct buy iff alpha > {fmt(a_star)}; naive buy iff alpha > 3/5")
    print(f"decision flips for alpha in ({fmt(a_star)}, 3/5); at alpha=1/2 "
          f"correct=Q2={fmt(closed(3, F(1, 2))[3])}, naive=1/2")
    print()

    print("=== N=5 transfer, alpha=1/2 ===")
    e = exact(5, F(1, 2))
    print(f"Q1={fmt(e['Q1'])} (control), Q2={fmt(e['Q2'])} (correct), "
          f"naive Q2={fmt(e['naive_Q2'])}")
    print(f"price t=3/5: correct {'buy' if e['Q2'] > F(3, 5) else 'refuse'}, "
          f"naive {'buy' if e['naive_Q2'] > F(3, 5) else 'refuse'}")
    print()

    print("=== Sanity: Q1 under the classical informed host (for contrast) ===")
    # Classical K: uniform over empty unchosen doors.  With 3 doors:
    # prize A -> opens B or C with 1/2; prize C -> opens B; prize B -> opens C.
    pE = F(1, 3) * F(1, 2) + F(1, 3) * 1
    q1 = F(1, 3) * 1 / pE
    print(f"classical informed host, P(C|B open empty)={fmt(q1)} (known 2/3)")
    assert q1 == F(2, 3)
    print("All exact checks passed.")


if __name__ == "__main__":
    main()
