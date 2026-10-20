"""r59: finite minimax over a finite class of fifth strategies.

Finite class: correct, prior, equal, classic, plus fixed shifts
alpha+delta_j for delta_j in a finite set.  Each pair is analytic; if not
identically equal, its collision set is finite; a finite union is finite, so
there is an alpha with all values distinct and the robust margin is positive.

Contrast: the continuous interval [0.02,0.20] has a positive but lower margin
(about 0.0099); the unbounded class has zero (the collision delta_c can be
chosen for every alpha).
"""
import sys

sys.dont_write_bytecode = True


def f(alpha):
    return 2 * alpha / (1 + alpha)


def values(alpha, shifts):
    return [f(alpha), alpha, 0.5, 2 / 3] + [alpha + d for d in shifts]


def margin_class(alpha, shifts):
    vals = sorted(values(alpha, shifts))
    return min(vals[i + 1] - vals[i] for i in range(len(vals) - 1))


def continuous_margin(alpha, dmin, dmax, step=0.001):
    # if no delta is valid, the class reduces to the four hypotheses
    best = margin_class(alpha, [])
    d = dmin
    while d <= dmax + 1e-12:
        if alpha + d <= 1:
            best = min(best, margin_class(alpha, [d]))
        d += step
    return best


def main():
    print("=== r59 finite minimax ===")
    shifts = [0.02, 0.05, 0.10, 0.15, 0.20]
    best = (0.0, None)
    for i in range(1, 1000):
        a = i / 1000
        m = margin_class(a, shifts)
        if m > best[0]:
            best = (m, a)
    print(f"finite class {shifts}")
    print(f"  robust alpha={best[1]:.3f}, margin={best[0]:.6f}")
    assert best[0] > 0
    # compare with the four-hypothesis optimum
    print(f"  four-hypothesis optimum 0.140388")
    # continuous bounded class: positive but lower than the finite class
    cont_best = (0.0, None)
    for i in range(1, 1000):
        a = i / 1000
        if a + 0.02 > 1:
            continue
        m = continuous_margin(a, 0.02, 0.20)
        if m > cont_best[0]:
            cont_best = (m, a)
    print(f"continuous class [0.02,0.20]: robust alpha={cont_best[1]:.3f}, "
          f"margin={cont_best[0]:.6f}")
    assert 0 < cont_best[0] < best[0]
    # a finite class with a single shift also has a positive margin at a separating alpha
    one = margin_class(0.37, [0.02])
    print(f"finite class with one shift 0.02 at alpha=0.37: margin={one:.6f}")
    assert one > 0
    print("All checks passed")


if __name__ == "__main__":
    main()
