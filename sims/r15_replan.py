"""P19: классическая защита (перепланирование с квотой k) при неравных априорах.

Без защиты: ведущий открывает k коз, равновероятно среди всех коз (включая вашу дверь).
С защитой: k коз среди чужих дверей. Обязательный выбор. Точные дроби.
Порог: защита выгодна <=> p0/p < T = (N-1)/(N-1-k) - k/(N-k).
"""
from fractions import Fraction as F

from r10_deletion import exch, protected, quota_law, replan, win


def formulas(N, k, p0):
    p = (1 - p0) / (N - 1)
    unp = max(p0, p) + p * k / (N - k) if p0 >= p else None
    prot = max(p0, p * F(N - 1, N - 1 - k))
    return unp, prot


if __name__ == "__main__":
    n = 0
    for N in (3, 4, 5, 6):
        for k in range(1, N - 1):
            T = F(N - 1, N - 1 - k) - F(k, N - k)
            for p0 in [F(j, 60) for j in range(20, 60)]:
                p = (1 - p0) / (N - 1)
                if p0 < p:
                    continue
                pr = [p0] + [p] * (N - 1)
                u = win(N, pr, exch(N, quota_law(N, k)))
                r = protected(N, pr, replan(N, k, F(1)))
                assert (u, r) == formulas(N, k, p0)
                assert (r > u) == (p0 / p < T) and (r == u) == (p0 / p == T)
                n += 1
    pr = [F(1, 2), F(1, 4), F(1, 4)]
    assert (win(3, pr, exch(3, quota_law(3, 1))), protected(3, pr, replan(3, 1, F(1)))) == (F(5, 8), F(1, 2))
    assert (win(3, [F(1, 3)] * 3, exch(3, quota_law(3, 1))), protected(3, [F(1, 3)] * 3, replan(3, 1, F(1)))) == (F(1, 2), F(2, 3))
    print(f"P19: {n} точных случаев; порог T подтверждён; (1/2,1/4,1/4): 5/8 -> 1/2, равные: 1/2 -> 2/3.")
    print("ALL OK")
