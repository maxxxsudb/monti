"""r63: Fisher block-diagonal check under target invariance.

Model: K in {0,1}, pi=1/2, P(E=1|K=1)=alpha, P(E=1|K=0)=1/2;
Y in {0,1}, P(Y=1|E)=theta, Y independent of K given E.
Then P(Y,E)=P_theta(Y|E) M_alpha(E), M_alpha(1)=alpha/2+1/4.
The Fisher matrix for (theta,alpha) is computed by finite differences and
compared with the exact blocks:
  I_tt = 1/(theta(1-theta))
  I_aa = M'(alpha)^2 / (M(alpha)(1-M(alpha)))
  I_ta = 0
"""
import sys
import math

sys.dont_write_bytecode = True


def bern(y, p):
    return p if y == 1 else 1 - p


def M(e, alpha):
    m1 = alpha / 2 + 1 / 4
    return m1 if e == 1 else 1 - m1


def P(y, e, theta, alpha):
    return bern(y, theta) * M(e, alpha)


def logP(y, e, theta, alpha):
    return math.log(P(y, e, theta, alpha))


def fisher(theta, alpha, h=1e-6):
    """Finite-difference observed Fisher matrix for one observation."""
    params = (theta, alpha)
    I = [[0.0, 0.0], [0.0, 0.0]]
    for y in (0, 1):
        for e in (0, 1):
            p = P(y, e, theta, alpha)
            d = [0.0, 0.0]
            for k in range(2):
                tp = list(params)
                tm = list(params)
                tp[k] += h
                tm[k] -= h
                d[k] = (logP(y, e, *tp) - logP(y, e, *tm)) / (2 * h)
            for i in range(2):
                for j in range(2):
                    I[i][j] += p * d[i] * d[j]
    return I


def main():
    print("=== r63 Fisher block-diagonal ===")
    checks = 0
    for theta, alpha in ((0.5, 0.5), (0.3, 0.2), (0.7, 0.8)):
        I = fisher(theta, alpha)
        m1 = alpha / 2 + 1 / 4
        expected_tt = 1 / (theta * (1 - theta))
        expected_aa = 0.25 / (m1 * (1 - m1))
        print(f"theta={theta}, alpha={alpha}")
        print(f"  Fisher[0][0]={I[0][0]:.6f} (expected {expected_tt:.6f})")
        print(f"  Fisher[1][1]={I[1][1]:.6f} (expected {expected_aa:.6f})")
        print(f"  Fisher[0][1]={I[0][1]:.3e}")
        assert abs(I[0][0] - expected_tt) < 1e-4
        assert abs(I[1][1] - expected_aa) < 1e-4
        assert abs(I[0][1]) < 1e-6
        checks += 3
    print(f"All checks passed; total: {checks}")


if __name__ == "__main__":
    main()
