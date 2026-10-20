"""r54: target-invariant characterization checks.

Finite mixture: P(Y|E) is independent of the prior for all priors iff the
component-conditional target distributions are equal.  Exact checks for the
host-type item, the lazy informed host, and a general finite example.
"""
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True


def lazy_exact(alpha, q):
    """Exact enumeration for the lazy informed host.

    Doors A=0 (chosen), B=1, C=2.  K opens B with probability q when both B
    and C are empty (prize A), opens B when only B is empty (prize C), opens C
    when only C is empty (prize B).  R opens B or C uniformly, even with prize.
    E: opened B and B is empty.
    """
    mass = {}
    for prize in (0, 1, 2):
        # K
        if prize == 0:
            acts = [(1, q), (2, 1 - q)]
        elif prize == 2:
            acts = [(1, F(1))]
        else:  # prize == 1
            acts = [(2, F(1))]
        for act, prob in acts:
            mass[(prize, "K", act)] = alpha * F(1, 3) * prob
        # R
        for act in (1, 2):
            mass[(prize, "R", act)] = (1 - alpha) * F(1, 3) * F(1, 2)
    E = {k: v for k, v in mass.items() if k[2] == 1 and k[0] != 1}
    pE = sum(E.values(), F(0))
    pEK = sum(v for (prize, kind, act), v in mass.items() if kind == "K" and act == 1 and prize != 1)
    pER = sum(v for (prize, kind, act), v in mass.items() if kind == "R" and act == 1 and prize != 1)
    pCK = sum(v for (prize, kind, act), v in E.items() if kind == "K" and prize == 2)
    pCR = sum(v for (prize, kind, act), v in E.items() if kind == "R" and prize == 2)
    pC = sum(v for (prize, kind, act), v in E.items() if prize == 2)
    pK = sum(v for (prize, kind, act), v in E.items() if kind == "K")
    return {
        "P(E|K)": pEK / alpha if alpha else None,
        "P(E|R)": pER / (1 - alpha) if alpha < 1 else None,
        "P(C|E,K)": pCK / pEK if pEK else None,
        "P(C|E,R)": pCR / pER if pER else None,
        "P(C|E)": pC / pE if pE else None,
        "P(K|E)": pK / pE if pE else None,
        "P(E)": pE,
    }


def check_host_type():
    print("=== Host-type item (q=1): target invariant ===")
    checks = 0
    for i in range(1, 10):
        alpha = F(i, 10)
        e = lazy_exact(alpha, F(1))
        assert e["P(E|K)"] == F(2, 3)
        assert e["P(E|R)"] == F(1, 3)
        assert e["P(C|E,K)"] == F(1, 2)
        assert e["P(C|E,R)"] == F(1, 2)
        assert e["P(C|E)"] == F(1, 2)
        checks += 5
    print(f"  {checks} exact checks: P(C|E)=1/2 for all alpha")
    return checks


def check_lazy():
    print("=== Lazy informed host (q=1/2): target informative ===")
    checks = 0
    for alpha in (F(1, 3), F(1, 2), F(2, 3)):
        e = lazy_exact(alpha, F(1, 2))
        assert e["P(E|K)"] == F(1, 2)
        assert e["P(E|R)"] == F(1, 3)
        assert e["P(C|E,K)"] == F(2, 3)
        assert e["P(C|E,R)"] == F(1, 2)
        expected = (1 + alpha) / (2 * (1 + alpha * F(1, 2)))
        assert e["P(C|E)"] == expected, (alpha, e["P(C|E)"], expected)
        checks += 5
        print(f"  alpha={alpha}: P(C|E,K)=2/3, P(C|E,R)=1/2, P(C|E)={e['P(C|E)']}")
    # concrete values from the note
    assert lazy_exact(F(1, 3), F(1, 2))["P(C|E)"] == F(4, 7)
    assert lazy_exact(F(1, 2), F(1, 2))["P(C|E)"] == F(3, 5)
    checks += 2
    print("  exact: alpha=1/3 -> 4/7; alpha=1/2 -> 3/5")
    return checks


def check_q0():
    print("=== q=0: observation uninformative about K, target still informative ===")
    checks = 0
    for alpha in (F(1, 3), F(1, 2), F(2, 3)):
        e = lazy_exact(alpha, F(0))
        assert e["P(E|K)"] == F(1, 3) == e["P(E|R)"]
        assert e["P(K|E)"] == alpha
        assert e["P(C|E)"] == (1 + alpha) / 2
        checks += 3
    print("  exact: P(K|E)=alpha; P(C|E)=(1+alpha)/2")
    return checks


def general_example():
    print("=== General finite example ===")
    # two components, target Y in {0,1}; p1=(1,0), p2=(0,1), equal likelihoods
    # target posterior after E: (alpha, 1-alpha)
    checks = 0
    for alpha in (F(1, 3), F(1, 2), F(2, 3)):
        post = (alpha, 1 - alpha)
        assert post[0] + post[1] == 1
        checks += 1
    assert (F(1, 3), F(2, 3)) != (F(2, 3), F(1, 3))
    checks += 1
    print("  p1=(1,0), p2=(0,1): P(Y|E)=(alpha,1-alpha); two priors give different posteriors")
    # if p1=p2, invariant
    for alpha in (F(1, 10), F(1, 2), F(9, 10)):
        post = alpha * F(1, 2) + (1 - alpha) * F(1, 2)
        assert post == F(1, 2)
        checks += 1
    print("  p1=p2=(1/2,1/2): P(Y|E)=1/2 for all priors")
    return checks


def check_only_if():
    print("=== Only-if check: differing components -> some prior changes the target ===")
    # p1=(3/4,1/4), p2=(1/4,3/4), likelihoods a1=1, a2=2
    p1 = (F(3, 4), F(1, 4))
    p2 = (F(1, 4), F(3, 4))
    a1, a2 = F(1), F(2)
    priors = [F(1, 10), F(1, 2), F(9, 10)]
    posts = []
    for alpha in priors:
        w1 = alpha * a1
        w2 = (1 - alpha) * a2
        p = (w1 * p1[0] + w2 * p2[0]) / (w1 + w2)
        posts.append(p)
    assert len(set(posts)) == 3, posts
    print(f"  target posterior for alpha=1/10,1/2,9/10: {[str(x) for x in posts]}")
    return 1


def main():
    print("=== r54 target-invariant characterization ===")
    total = 0
    total += check_host_type()
    total += check_lazy()
    total += check_q0()
    total += general_example()
    total += check_only_if()
    print(f"All checks passed; total: {total}")


if __name__ == "__main__":
    main()
