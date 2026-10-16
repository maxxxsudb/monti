"""P11: защита как вычёркивание из плана ведущего; квота и перепланирование; граница по априору.

N дверей, машина по априору p, вы держите дверь 0. Ведущий знает, где машина, и выбирает
план S — множество дверей с козами (ваша дверь тоже может войти). Без защиты он открывает S.
Защита-вычёркивание: открывает S без двери 0. Защита-перепланирование (квота k): если машина
не у вас, открывает равновероятное k-подмножество из N-2 доступных дверей с козами.
Выбор обязательный и оптимальный. Всё в точных дробях.
"""
from fractions import Fraction as F
from itertools import combinations
from math import comb


def subsets(xs):
    for k in range(len(xs) + 1):
        for s in combinations(xs, k):
            yield frozenset(s)


def win(N, prior, plan, observe=lambda S: S):
    obs = {}
    for c in range(N):
        for S, p in plan(c).items():
            v = obs.setdefault(observe(S), [F(0)] * N)
            v[c] += prior[c] * p
    return sum(max(v[d] for d in range(N) if d not in o) for o, v in obs.items())


def protected(N, prior, plan):
    return win(N, prior, plan, lambda S: S - {0})


def exch(N, w):
    """Перестановочный план: размер k с вероятностью w[k], множество равновероятно."""
    def plan(c):
        goats = [d for d in range(N) if d != c]
        return {S: w[len(S)] / comb(N - 1, len(S)) for S in subsets(goats)}
    return plan


def coin_law(N, q):
    return [comb(N - 1, k) * q**k * (1 - q) ** (N - 1 - k) for k in range(N)]


def quota_law(N, k):
    return [F(int(j == k)) for j in range(N)]


def replan(N, k, lam):
    """Квота k; при защите и козе у вас с вероятностью lam ведущий перепланирует,
    иначе просто вычёркивает вашу дверь из исходного плана."""
    base = exch(N, quota_law(N, k))

    def plan(c):
        if c == 0:
            return base(c)
        out = {}
        for S, p in base(c).items():  # вычёркивание с весом 1-lam
            out[S - {0}] = out.get(S - {0}, 0) + (1 - lam) * p
        elig = [d for d in range(1, N) if d != c]
        for S in combinations(elig, k):  # перепланирование с весом lam
            S = frozenset(S)
            out[S] = out.get(S, 0) + lam / comb(N - 2, k)
        return out
    return plan


if __name__ == "__main__":
    # 1. Лемма вычёркивания: перестановочный план и p0 <= остальных => защита ничего не стоит.
    laws = {N: [coin_law(N, F(1, 2)), coin_law(N, F(1, 3)), coin_law(N, F(3, 4))]
            + [quota_law(N, k) for k in range(N)]
            + [[F(1, N)] * N, [F(0)] * (N - 2) + [F(1, 2), F(1, 2)]] for N in (3, 4, 5)}
    priors = {3: [[F(1, 3)] * 3, [F(1, 5), F(2, 5), F(2, 5)], [F(1, 6), F(1, 3), F(1, 2)]],
              4: [[F(1, 4)] * 4, [F(1, 10), F(2, 10), F(3, 10), F(4, 10)]],
              5: [[F(1, 5)] * 5, [F(1, 9), F(2, 9), F(2, 9), F(2, 9), F(2, 9)]]}
    n = 0
    for N in (3, 4, 5):
        for w in laws[N]:
            for pr in priors[N]:
                assert protected(N, pr, exch(N, w)) == win(N, pr, exch(N, w))
                n += 1
    print(f"P11: {n} точных совпадений (N=3..5, монетки, квоты, смеси, p0 <= остальных).")

    # Вычёркивание — огрубление: никогда не помогает; без перестановочности — строгая потеря.
    # Ведущий бросает монетку только над вашей дверью (если там коза).
    only0 = lambda c: {frozenset(): F(1)} if c == 0 else {frozenset([0]): F(1, 2), frozenset(): F(1, 2)}
    a, b = protected(3, [F(1, 3)] * 3, only0), win(3, [F(1, 3)] * 3, only0)
    assert (a, b) == (F(1, 3), F(1, 2))
    print(f"Неперестановочный план (монетка только над вашей дверью): защита {a} < без защиты {b}.")

    # 2. Разложение классики: вычёркивание 0 + перепланирование; ручка lam даёт 1/2 + lam/6.
    for lam in (F(0), F(1, 4), F(1, 2), F(1)):
        assert protected(3, [F(1, 3)] * 3, replan(3, 1, lam)) == F(1, 2) + lam / 6
    for N in (3, 4, 5, 6):
        for k in range(N - 1):
            pr = [F(1, N)] * N
            assert win(N, pr, exch(N, quota_law(N, k))) == F(1, N - k)
            assert protected(N, pr, replan(N, k, F(1))) == F(N - 1, N * (N - 1 - k))
    print("Классика: 1/2 (вычёркивание) + lam/6 (перепланирование); квота k: 1/(N-k) -> (N-1)/(N(N-1-k)).")

    # 3. Граница по априору: N=3, монетка q=1/2, априор (p0, p, p) — «палатка» потерь.
    def tent(p0):
        prot = (3 - 2 * p0) / 4 if p0 <= F(1, 2) else p0
        unp = (3 - 2 * p0) / 4 if p0 <= F(1, 3) else (3 + 5 * p0) / 8
        return prot, unp
    for p0 in [F(j, 60) for j in range(0, 61, 3)]:
        pr = [p0, (1 - p0) / 2, (1 - p0) / 2]
        got = (protected(3, pr, exch(3, coin_law(3, F(1, 2)))), win(3, pr, exch(3, coin_law(3, F(1, 2)))))
        assert got == tent(p0), (p0, got)
    print("Граница: потеря 0 при p0<=1/3, 9/8(p0-1/3) на [1/3,1/2], 3(1-p0)/8 на [1/2,1].")
    print("ALL OK")
