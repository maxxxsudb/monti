"""r49b: minimal adaptive protocol for the host-type item.

Item (exact key in r49_protocol_type.py): N=3, prize uniform behind A/B/C,
subject chose A, host opened B and B is empty.  Before the game the host is
informed (K) with probability alpha, otherwise uninformed (R).  K always
opens B when B is empty; if the prize is behind B he opens C.  R opens B or
C uniformly, even if the prize is there.

Question Q2:  P(host was informed | observed empty B).

Four behavioural hypotheses about a subject's answer to Q2:

  correct   f(a) = 2a/(1+a)   proper posterior (likelihood ratio 2)
  prior     a                 ignores the observation, reports the prior
  equal     1/2               ignores the host type, uses "two doors left"
  classic   2/3               transplants the classical Monty answer

At alpha=1/4 the four predicted answers are

  correct 2/5, prior 1/4, equal 1/2, classic 2/3,

all distinct.  So ONE direct question separates the four hypotheses.  This
is the minimum possible (zero questions cannot separate anything).

Collisions to avoid:
  alpha=1/3: correct = equal = 1/2
  alpha=1/2: correct = classic = 2/3, prior = equal = 1/2
  alpha=2/3: prior = classic = 2/3
The current pilot's alpha=1/3 point is exactly a collision for this item,
which is why the one-question design must choose a different prior.
"""
from fractions import Fraction as F

HYP = ["correct", "prior", "equal", "classic"]


def q2(h, alpha):
    a = F(alpha)
    if h == "correct":
        return 2 * a / (1 + a)
    if h == "prior":
        return a
    if h == "equal":
        return F(1, 2)
    if h == "classic":
        return F(2, 3)
    raise ValueError(h)


def q1(h):
    """Prize question P(C | B empty).  It is 1/2 for the first three; a
    classical-pattern responder may answer 2/3.  It is a control, not the
    main identifier."""
    return F(2, 3) if h == "classic" else F(1, 2)


def price(h, alpha, t=F(3, 5)):
    return "buy" if q2(h, alpha) > t else ("indiff" if q2(h, alpha) == t else "refuse")


def table(alpha):
    return {h: q2(h, alpha) for h in HYP}


def main():
    print("=== Exact collision map for Q2 ===")
    print("correct = 2a/(1+a), prior = a, equal = 1/2, classic = 2/3")
    print("Solving each equality exactly:")
    print("  correct = equal   <=> 2a/(1+a) = 1/2  <=> a = 1/3")
    print("  correct = classic <=> 2a/(1+a) = 2/3  <=> a = 1/2")
    print("  prior   = equal   <=> a = 1/2")
    print("  prior   = classic <=> a = 2/3")
    print("  correct = prior   <=> a = 0 or a = 1 (degenerate controls)")
    print("For 0<a<1, any alpha outside {1/3, 1/2, 2/3} separates all four.")
    assert q2("correct", F(1, 3)) == q2("equal", F(1, 3))
    assert q2("correct", F(1, 2)) == q2("classic", F(1, 2))
    assert q2("prior", F(1, 2)) == q2("equal", F(1, 2))
    assert q2("prior", F(2, 3)) == q2("classic", F(2, 3))
    assert q2("correct", F(0)) == q2("prior", F(0))
    assert q2("correct", F(1)) == q2("prior", F(1))
    print("(six exact equalities checked)")
    print()

    print("=== One-question design at alpha=1/4 ===")
    vals = table(F(1, 4))
    for h in HYP:
        print(f"  {h:>8}: {vals[h]}")
    assert len(set(vals.values())) == 4
    print("Four distinct answers: one question identifies the hypothesis.")
    print()

    print("=== One-question design at alpha=2/5 (larger correct-prior gap) ===")
    vals = table(F(2, 5))
    for h in HYP:
        print(f"  {h:>8}: {vals[h]}")
    assert len(set(vals.values())) == 4
    print("Also four distinct answers; correct-prior gap = 6/35 ~ 0.171.")
    print()

    print("=== Why the current card's alpha=1/3 is not a separating prior ===")
    vals = table(F(1, 3))
    for h in HYP:
        print(f"  {h:>8}: {vals[h]}")
    print("correct and equal both answer 1/2: one question cannot separate them.")
    print()

    print("=== Choosing the prior: maximum minimum separation ===")
    def min_gap(a):
        vals = sorted(table(F(a)).values())
        return min(vals[i + 1] - vals[i] for i in range(len(vals) - 1))

    best = (F(-1), None)
    for i in range(1, 1000):
        a = F(i, 1000)
        g = min_gap(a)
        if g > best[0]:
            best = (g, a)
    print(f"grid optimum: alpha={best[1]} ({float(best[1]):.4f}), "
          f"minimum gap={best[0]} ({float(best[0]):.4f})")
    print("exact optimum solves 2a^2-5a+1=0: alpha=(5-sqrt(17))/4 ~ 0.2192")
    print("simple near-optimal choice alpha=2/9:")
    for h in HYP:
        print(f"  {h:>8}: {q2(h, F(2, 9))}")
    print(f"  minimum gap = {min_gap(F(2, 9))} ({float(min_gap(F(2, 9))):.4f})")
    print()

    print("=== Price probe at alpha=1/4, price 3/5 ===")
    for h in HYP:
        print(f"  {h:>8}: Q2={str(q2(h, F(1, 4))):>4} -> {price(h, F(1, 4))}")
    print("The price separates classic (buy) from the other three (refuse),")
    print("but not correct from prior/equal.  It measures consequences, not identity.")
    print()

    print("=== Two-question fallback for an off-key answer ===")
    print("Ask Q2 at 1/4; if the answer is one of 1/4, 2/5, 1/2, 2/3, stop.")
    print("Otherwise ask Q2 at 1/2 and/or the prize question Q1; the pair")
    print("(Q2@1/4, Q2@1/2) has the following code:")
    for h in HYP:
        print(f"  {h:>8}: ({q2(h, F(1, 4))}, {q2(h, F(1, 2))})")
    print("correct=(2/5,2/3), prior=(1/4,1/2), equal=(1/2,1/2), classic=(2/3,2/3).")
    print("These four pairs are distinct as well: a two-question code without")
    print("choosing a separating prior, useful if the first answer is approximate.")
    print()

    print("=== Minimality ===")
    print("One question is the minimum.  A single question at a separating")
    print("prior achieves it.  Two questions are needed only to guard against")
    print("an off-key answer or a constant responder; the pair above is one")
    print("such guard, at the cost of a second direct appeal.")


if __name__ == "__main__":
    main()
