"""Резонанс штрафа: монетка Монти, равные априоры, право уйти (+1 / -g / 0).

Предсказание: защита бесплатна <=> 1/g целое или g <= 1/(N-1).
Точные дроби: прямой перебор наблюдений (без защиты и с вычёркиванием).
"""
from fractions import Fraction as F
from itertools import combinations


def values(N, q, g):
    p = F(1, N)
    U = P = F(0)
    for k in range(1, N + 1):  # без защиты: S — закрытые двери, машина в S
        for S in combinations(range(N), k):
            ws = [p * (1 - q) ** (k - 1) * q ** (N - k) if c in S else 0 for c in range(N)]
            U += max(0, max((1 + g) * w - g * sum(ws) for w in ws))
    for k in range(0, N):      # с защитой: дверь 0 всегда закрыта, C — закрытые соперники
        for C in combinations(range(1, N), k):
            ws = [0] * N
            ws[0] = p * (1 - q) ** k * q ** (N - 1 - k)
            for d in C:
                ws[d] = p * (1 - q) ** (k - 1) * q ** (N - 1 - k)
            P += max(0, max((1 + g) * w - g * sum(ws) for w in ws))
    return U, P


def predicted_free(N, g):
    return (1 / g).denominator == 1 or g <= F(1, N - 1)


def closed_loss(N, q, g):
    """Сумма зазоров по числу c закрытых соперников (вывод в PROOFS)."""
    p, L = F(1, N), 1 / (1 - q)
    tot = F(0)
    for c in range(1, N):
        line = lambda w0: (1 + g) * L * p - g * (c * L * p + w0)   # «играть за соперника»
        F2 = lambda w0: max(0, line(w0), w0 - g * c * L * p)
        gap = q * F2(0) + (1 - q) * F2(L * p) - F2(p)
        tot += F(len(list(combinations(range(N - 1), c)))) * (1 - q) ** c * q ** (N - 1 - c) * gap
    return tot


if __name__ == "__main__":
    n = 0
    for N in (3, 4, 5, 6):
        for q in (F(1, 3), F(1, 2), F(4, 5)):
            for g in [F(1, 7), F(1, 5), F(1, 4), F(3, 10), F(1, 3), F(2, 5), F(1, 2), F(3, 5), F(2, 3),
                      F(3, 4), F(1), F(6, 5), F(3, 2), F(2), F(3)]:
                U, P = values(N, q, g)
                assert (U == P) == predicted_free(N, g), (N, q, g, U - P)
                assert U - P == closed_loss(N, q, g), (N, q, g)
                n += 1
    print(f"Резонанс: бесплатно <=> 1/g целое или g <= 1/(N-1); {n} точных случаев, формула потерь совпала.")
    for g, L in ((F(3, 5), F(1, 60)), (F(2, 3), F(1, 36)), (F(9, 10), F(1, 120)), (F(1), 0), (F(2), F(1, 6))):
        U, P = values(3, F(1, 2), g)
        assert U - P == L
    print("N=3, q=1/2: палатка (2g-1)/12, (1-g)/12, (g-1)/6; 2/3 -> 1/36, 9/10 -> 1/120.")
    print("ALL OK")
