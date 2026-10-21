"""Exact examples and interval invariants for the October 21 review."""
from fractions import Fraction as F
from itertools import combinations
from math import ceil, log, log2


def product(values):
    result = F(1)
    for value in values:
        result *= value
    return result


def repairs():
    defects = ((), (0,), (1,), (2,), (0, 1))
    names = ("N", "L", "W", "E", "LW")
    q, t = F(9, 10), F(1, 10)
    rows = [tuple(product(q if d == i else t for d in ds) for i in range(3))
            for ds in defects]
    assert rows[-1] == (F(9, 100), F(9, 100), F(1, 100))
    for name, row in zip(names, rows):
        print("repair profile", name, ",".join(map(str, row)))
    for eps in (F(0), F(1, 10), F(1, 4), F(1, 2), F(3, 4)):
        for rho in (F(0), F(1, 10), F(3, 10), F(1, 2)):
            if eps + rho < F(1, 2):
                high, low = 1 - eps - rho, eps + rho
                assert high > F(1, 2) > low
                assert high - low == 1 - 2 * eps - 2 * rho
            else:
                q0 = 1 - eps if eps <= F(1, 2) else F(1, 2)
                t0 = eps if eps <= F(1, 2) else F(1, 2)
                assert q0 >= 1 - eps and t0 <= eps
                for width in range(4):
                    for selected in combinations(range(3), width):
                        pL = q0 if 0 in selected else t0
                        pW = q0 if 1 in selected else t0
                        common = (pL + pW) / 2
                        assert abs(common - pL) <= rho
                        assert abs(common - pW) <= rho
    print("Repair threshold and matching L/W channels for every intervention subset: PASS")


def boundary_invariant():
    checks = 0
    mu, tau = F(1, 2), F(1, 2)
    eta = F(1, 32)
    for root in [F(i, 40) for i in range(41)]:
        intervals = {(F(0), F(1))}
        for stage in range(4):
            next_intervals = set()
            for a, b in intervals:
                radius, mid = b - a, (a + b) / 2
                tolerance = mu * radius / 8
                true_w = tau + mu * (mid - root)
                for error in (-tolerance, F(0), tolerance):
                    estimate = true_w + error
                    if estimate > tau + tolerance:
                        new = a, mid
                    elif estimate < tau - tolerance:
                        new = mid, b
                    else:
                        new = mid - radius / 4, mid + radius / 4
                    assert new[0] <= root <= new[1]
                    assert new[1] - new[0] == radius / 2
                    next_intervals.add(new)
                    checks += 1
            intervals = next_intervals
        assert all(abs((a + b) / 2 - root) <= eta for a, b in intervals)
    print("Boundary interval invariants under bounded estimation errors:", checks, "PASS")
    delta, mu, eta, beta = .5, .5, .05, .05
    stages = max(0, ceil(log2(1 / (2 * eta))))
    counts = [ceil(32 * 4**j / (delta**2 * mu**2)
                   * log(2 / (beta * 2**(j - stages)))) for j in range(stages)]
    print("Own conservative budget example: stages=", stages,
          "counts=", counts, "total=", sum(counts))


def unknown_tents():
    L, eta = F(1), F(1, 10)
    count = int(L / (2 * eta))
    centers = [(2 * j - 1) * eta / L for j in range(1, count + 1)]
    for center in centers:
        bump = lambda x: max(F(0), eta - L * abs(x - center))
        assert bump(center) == eta
        assert bump(center - eta / L) == bump(center + eta / L) == 0
        assert F(1, 4) + bump(center) <= F(3, 8)
    assert all(b - a >= 2 * eta / L for a, b in zip(centers, centers[1:]))
    print("Disjoint Bernoulli UNKNOWN tents:", count, "PASS")
    blue = F(2, 5)
    evidence = blue + (1 - blue) * F(1, 3)
    assert evidence == F(3, 5) and blue / evidence == F(2, 3)
    for t, T in ((F(1), F(3)), (F(2), F(5))):
        cutoff = t / (T + t)
        for prior in (F(1, 10), F(2, 5), F(3, 5)):
            post = prior / (prior + (1 - prior) * t / T)
            assert (post > F(1, 2) > prior) == (cutoff < prior < F(1, 2))
    print("Lamp posteriors, event frequency and general reversal condition: PASS")


if __name__ == "__main__":
    repairs()
    boundary_invariant()
    unknown_tents()
    print("PASS; these finite checks supplement the proofs, not the missing source runs")
