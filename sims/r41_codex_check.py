from fractions import Fraction as F
from math import comb

from r41_rent import classic_msgs, messages, rent0, stealth


def coin_closed_form(n, p0, q):
    p, s = (1 - p0) / n, 1 - q
    loss = tv = F(0)
    for k in range(n + 1):
        a = p0 * s**k * q ** (n - k)
        b = p * s ** (k - 1) * q ** (n - k) if k else F(0)
        mass = a + k * b
        naive_a = p0 / (p0 + k * p)
        tv += comb(n, k) * abs(a - mass * naive_a)
        if not k:
            chosen = a
        elif p0 > p:
            chosen = a
        elif p0 < p:
            chosen = b
        else:
            chosen = min(a, b)
        loss += comb(n, k) * (max(a, b) - chosen)
    return loss, tv


if __name__ == '__main__':
    count = 0
    for N in range(3, 8):
        for p0 in (F(1, 2 * N), F(1, N), F(2, 5), F(1, 2), F(51, 100), F(3, 4)):
            p = (1 - p0) / (N - 1)
            pr = [p0] + [p] * (N - 1)
            for q in (F(1, 7), F(1, 2), F(6, 7)):
                loss, tv, inv = stealth(pr, messages(pr, q))
                assert (loss, tv) == coin_closed_form(N - 1, p0, q)
                assert loss <= 2 * tv
                if inv:
                    assert tv <= 1 - F(1, N)
                if N == 3 and p0 == F(1, 3):
                    assert rent0(pr, q) == q * (q + 2) / 9
                count += 1
            if p0 > p:
                loss, tv, inv = stealth(pr, classic_msgs(pr, N - 2))
                assert loss == max(p0, 1 - p0) - p0
                assert tv == abs(p0 / (p0 + p) - p0)
                assert inv == (p0 >= F(1, 2))
                count += 1
    p0, N = F(51, 100), 3
    assert stealth([p0, F(49, 200), F(49, 200)], classic_msgs([p0, F(49, 200), F(49, 200)], 1)) == (0, F(2499, 15100), True)
    print(f'PASS: {count} exact comparisons with count-based formulas; strict-choice example 2499/15100')
