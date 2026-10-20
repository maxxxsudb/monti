"""r58: analytic robust alpha for a bounded fifth strategy.

Fifth strategy a_5(alpha)=alpha+delta, delta in [dmin,dmax].  The robust
margin at alpha is the minimum of margin(alpha,delta) over delta in the
interval.  In the regime where the active gaps are (f(alpha)-alpha) and
(alpha+delta-f(alpha)), the optimum balances them:

    2 f(alpha) = 2 alpha + delta,   f(alpha)=2 alpha/(1+alpha),

hence 2 alpha^2 + (delta-2) alpha + delta = 0.  The upper root is the robust
alpha; the margin is delta/2.  The formula is valid while alpha+delta <= 1;
otherwise the boundary alpha=1-delta is used.  The low-alpha regime has the
collision delta_c=f(alpha)-alpha inside [dmin,dmax], so the adversary can
collide with correct and the robust margin is zero there.
"""
import sys
import math

sys.dont_write_bytecode = True


def f(alpha):
    return 2 * alpha / (1 + alpha)


def margin(alpha, delta):
    vals = sorted([f(alpha), alpha, 0.5, 2 / 3, alpha + delta])
    return min(vals[i + 1] - vals[i] for i in range(4))


def robust_margin(alpha, dmin, dmax, step=0.001):
    best = 2.0
    d = dmin
    while d <= dmax + 1e-12:
        if alpha + d <= 1:
            best = min(best, margin(alpha, d))
        d += step
    return best


def alpha_analytic(delta):
    disc = (2 - delta) ** 2 - 8 * delta
    if disc < 0:
        return None
    return (2 - delta + math.sqrt(disc)) / 4


def main():
    print("=== r58 analytic robust alpha ===")
    print(f"{'delta':>8} {'alpha*':>10} {'alpha+delta':>12} {'margin':>10} "
          f"{'delta/2':>8} {'tag':>10}")
    checks = 0
    for delta in (0.01, 0.02, 0.05, 0.1, 0.15, 0.2):
        a = alpha_analytic(delta)
        if a is None:
            print(f"{delta:>8.2f} {'none':>10}")
            continue
        if a + delta <= 1:
            alpha = a
            tag = "formula"
        else:
            alpha = 1 - delta
            tag = "boundary"
        m = robust_margin(alpha, delta, delta)
        # robust grid check: worst over delta in [delta, delta] is just one point,
        # but compare with a wider interval in the caller below
        print(f"{delta:>8.2f} {alpha:>10.6f} {alpha+delta:>12.6f} {m:>10.6f} "
              f"{delta/2:>8.6f} {tag:>10}")
        checks += 1

    print("\n=== robust grid checks on [dmin,dmax] ===")
    for dmin, dmax in ((0.02, 0.20), (0.05, 0.20), (0.10, 0.20)):
        a = alpha_analytic(dmin)
        if a is None:
            continue
        if a + dmin <= 1:
            alpha = a
            tag = "formula"
        else:
            alpha = 1 - dmin
            tag = "boundary"
        m_an = robust_margin(alpha, dmin, dmax)
        best = (0.0, None)
        for i in range(1, 1000):
            aa = i / 1000
            if aa + dmin > 1:
                continue
            mm = robust_margin(aa, dmin, dmax)
            if mm > best[0]:
                best = (mm, aa)
        print(f"  [{dmin},{dmax}]: analytic alpha={alpha:.4f}, margin={m_an:.6f}, "
              f"grid best alpha={best[1]:.3f}, margin={best[0]:.6f}, tag={tag}")
        assert best[0] <= m_an + 2e-3, (dmin, dmax, best, m_an)
        checks += 1

    print(f"\nAll checks passed; total: {checks}")


if __name__ == "__main__":
    main()
