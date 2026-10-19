"""r52: adaptive VOI checks.

  two-hypothesis value and cost threshold;
  continuation interval for a second probe;
  exact greedy-IG counterexample;
  host-type item: one vs two questions under symmetric answer noise.
"""
import sys
import os
import math
from fractions import Fraction as F

sys.dont_write_bytecode = True


def r0(pi):
    return min(pi, 1 - pi)


def r1(pi, p0, p1):
    """Bayes risk after one binary probe with prior pi."""
    P1 = pi * p1 + (1 - pi) * p0
    P0 = 1 - P1
    pi1 = pi * p1 / P1 if P1 > 0 else 0.0
    pi0 = pi * (1 - p1) / P0 if P0 > 0 else 0.0
    return P1 * min(pi1, 1 - pi1) + P0 * min(pi0, 1 - pi0)


def sym_value(pi, eps):
    return r0(pi) - r1(pi, eps, 1 - eps)


def check_two_hypotheses():
    print("=== Two hypotheses, symmetric probe ===")
    print(f"{'pi':>6} {'eps':>6} {'R0':>8} {'R1':>8} {'V':>8} {'V-(1/2-eps)':>14}")
    checks = 0
    for pi in (0.1, 0.3, 0.5, 0.7, 0.9):
        for eps in (0.1, 0.2, 0.3):
            v = sym_value(pi, eps)
            print(f"{pi:>6.2f} {eps:>6.2f} {r0(pi):>8.4f} {r1(pi, eps, 1-eps):>8.4f} "
                  f"{v:>8.4f} {v-(0.5-eps):>14.6f}")
            checks += 1
    v = sym_value(0.5, 0.1)
    assert abs(v - 0.4) < 1e-12
    assert abs(sym_value(0.5, 0.25) - 0.25) < 1e-12
    assert abs(sym_value(0.5, 0.5) - 0.0) < 1e-12
    print("  exact checks at pi=1/2: V=0.4, 0.25, 0 for eps=0.1,0.25,0.5")
    return checks + 3


def continuation(eps, c, step=0.001):
    qs = []
    q = step
    while q <= 0.5 + 1e-12:
        v = min(q, 1 - q) - r1(q, eps, 1 - eps)
        if v > c:
            qs.append(q)
        q += step
    if not qs:
        return None
    return (round(min(qs), 3), round(1 - min(qs), 3))


def check_continuation():
    print("\n=== Continuation interval for a second probe ===")
    print(f"{'eps':>6} {'c':>6} {'interval':>18}")
    checks = 0
    for eps in (0.1, 0.2):
        for c in (0.02, 0.05, 0.1):
            iv = continuation(eps, c)
            print(f"{eps:>6.2f} {c:>6.2f} {str(iv):>18}")
            checks += 1
    # sanity: at eps=0.1,c=0.05 the interval is nonempty and around 1/2
    iv = continuation(0.1, 0.05)
    assert iv is not None and iv[0] < 0.5 < iv[1]
    return checks + 1


def greedy_counterexample():
    print("\n=== Greedy information vs decision value ===")
    # decision d in {2,3}; losses as in the note
    prior_risk = F(1, 3)
    # Probe A: reveals H1 vs not-H1; no decision value
    risk_A = F(1, 3)
    value_A = prior_risk - risk_A
    cost_A = F(1, 100)
    net_A = value_A - cost_A
    ig_A = -(1 / 3) * math.log2(1 / 3) - (2 / 3) * math.log2(2 / 3)
    # Probe B: answers 0,2,3
    p0 = F(6, 10)
    p2 = F(2, 10)
    p3 = F(2, 10)
    # after '0': posterior (5/9,2/9,2/9); choose 2 or 3, loss 2/9
    loss_after_0 = F(2, 9)
    risk_B = p0 * loss_after_0
    value_B = prior_risk - risk_B
    cost_B = F(1, 10)
    net_B = value_B - cost_B
    h_b = -(F(5, 9) * math.log2(F(5, 9)) + 2 * F(2, 9) * math.log2(F(2, 9)))
    h_b = float(h_b)
    ig_B = math.log2(3) - float(p0) * h_b
    print(f"  prior risk = {float(prior_risk):.6f}")
    print(f"  A: IG={ig_A:.6f}, value={float(value_A):.6f}, cost={float(cost_A):.6f}, net={float(net_A):.6f}")
    print(f"  B: IG={ig_B:.6f}, value={float(value_B):.6f}, cost={float(cost_B):.6f}, net={float(net_B):.6f}")
    print(f"  B: H(H|B)={h_b:.6f}; P(0)={float(p0):.3f}, P(2)=P(3)={float(p2):.3f}")
    assert ig_A > ig_B, "A should have larger information"
    assert ig_A / float(cost_A) > ig_B / float(cost_B), "A should have larger IG/cost"
    assert value_A == 0
    assert abs(float(value_B) - 0.2) < 1e-12
    assert net_B > 0 > net_A
    print("  greedy IG and IG/cost pick A; optimal is B (B net > 0 > A net)")
    return 6


HYPS = ("correct", "prior", "equal", "classic")
KEYS = {
    "correct": F(2, 5),
    "prior": F(1, 4),
    "equal": F(1, 2),
    "classic": F(2, 3),
}
PAIRS = {
    "correct": (F(2, 5), F(2, 3)),
    "prior": (F(1, 4), F(1, 2)),
    "equal": (F(1, 2), F(1, 2)),
    "classic": (F(2, 3), F(2, 3)),
}


def coord_prob(obs, true, eps):
    if obs == true:
        return 1 - eps
    return eps / 3


def lik1(h, obs, eps):
    return coord_prob(obs, KEYS[h], eps)


def lik2(h, obs_pair, eps):
    return coord_prob(obs_pair[0], PAIRS[h][0], eps) * coord_prob(obs_pair[1], PAIRS[h][1], eps)


def bayes_risk(lik, observations, eps):
    total = sum(max(lik(h, obs, eps) for h in HYPS) for obs in observations)
    return 1 - total / len(HYPS)


def check_host_noise():
    print("\n=== Host-type item: one vs two questions under symmetric noise ===")
    obs1 = list(KEYS.values())
    obs2 = [(a, b) for a in KEYS.values() for b in KEYS.values()]
    print(f"{'eps':>6} {'R1':>10} {'R2':>10} {'reduction':>10}")
    checks = 0
    for eps in (F(0), F(1, 20), F(1, 10), F(1, 5), F(3, 10), F(2, 5), F(1, 2)):
        r1v = bayes_risk(lik1, obs1, eps)
        r2v = bayes_risk(lik2, obs2, eps)
        assert r1v == eps, (eps, r1v)
        assert r2v <= r1v + F(0)
        print(f"{float(eps):>6.2f} {float(r1v):>10.6f} {float(r2v):>10.6f} {float(r1v-r2v):>10.6f}")
        checks += 3
    # endpoint checks
    assert bayes_risk(lik1, obs1, F(0)) == 0
    assert bayes_risk(lik2, obs2, F(0)) == 0
    assert bayes_risk(lik1, obs1, F(1, 2)) == F(1, 2)
    assert bayes_risk(lik2, obs2, F(1, 2)) == F(1, 2)
    print("  exact checks: R1=eps; R2<=R1; eps=0 -> 0; eps=1/2 -> 1/2")
    return checks + 4


def main():
    print("=== r52 adaptive VOI ===")
    total = 0
    total += check_two_hypotheses()
    total += check_continuation()
    total += greedy_counterexample()
    total += check_host_noise()
    print(f"\nAll checks passed; total: {total}")


if __name__ == "__main__":
    main()
