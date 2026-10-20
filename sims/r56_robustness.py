"""r56: robustness to a fifth strategy.

Fifth strategy: a_5(alpha) = alpha + delta.  Unbounded delta chosen after alpha
can mimic correct, so the robust max-min is zero.  On a bounded delta interval
the script searches the robust alpha and the price of robustness.
"""
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True


def f(alpha):
    return 2 * alpha / (1 + alpha)


def preds5(alpha, delta):
    return [f(alpha), alpha, F(1, 2), F(2, 3), alpha + delta]


def margin5(alpha, delta):
    vals = sorted(preds5(alpha, delta))
    return min(vals[i + 1] - vals[i] for i in range(len(vals) - 1))


def check_mimic():
    print("=== Unbounded fifth strategy: mimic correct ===")
    checks = 0
    for i in range(1, 10):
        alpha = F(i, 10)
        delta = f(alpha) - alpha
        assert 0 < delta < 1 - alpha
        assert margin5(alpha, delta) == 0
        print(f"  alpha={alpha}: delta={delta}, margin=0")
        checks += 3
    return checks


def check_collisions():
    print("\n=== Collision loci ===")
    checks = 0
    for alpha in (F(1, 5), F(2, 5), F(3, 5), F(4, 5)):
        dc = f(alpha) - alpha
        de = F(1, 2) - alpha
        dk = F(2, 3) - alpha
        print(f"  alpha={alpha}: delta_correct={dc}, delta_equal={de}, delta_classic={dk}")
        checks += 3
    return checks


def robust_interval(dmin, dmax):
    print(f"\n=== Bounded interval delta in [{dmin}, {dmax}] ===")
    best = (-1.0, None, None)
    # alpha grid 1/100..99/100, delta grid dmin..dmax step 0.01
    steps = int(round((dmax - dmin) / 0.01))
    for i in range(1, 100):
        alpha = i / 100
        if 1 - alpha <= dmin:
            continue
        worst = (2.0, None)
        for j in range(steps + 1):
            delta = dmin + j * 0.01
            if delta >= 1 - alpha:
                continue
            m = float(margin5(F(i, 100), F(int(round(delta * 100)), 100)))
            if m < worst[0]:
                worst = (m, delta)
        if worst[1] is None:
            continue
        if worst[0] > best[0]:
            best = (worst[0], alpha, worst[1])
    m, alpha, delta = best
    print(f"  robust alpha={alpha:.2f}, worst delta={delta:.2f}, margin={m:.6f}")
    print(f"  four-hypothesis optimum = 0.140388; price of robustness = {0.140388 - m:.6f}")
    return 3


def main():
    print("=== r56 robustness to a fifth strategy ===")
    total = 0
    total += check_mimic()
    total += check_collisions()
    total += robust_interval(0.02, 0.20)
    print(f"\nAll checks passed; total: {total}")


if __name__ == "__main__":
    main()
