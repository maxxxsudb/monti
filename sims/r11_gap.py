"""P13: ценность проверки двери 0 = зазор Йенсена у атомов соперника; общий критерий нуля.

n дверей, одна цель, априор p_i. Двери из множества T проверяются независимыми одинаковыми
тестами с конечным числом исходов: g1 у цели, g0 у прочих, g0>0, l=g1/g0. Обязательный выбор.
Сравнивается: проверять ли дополнительно дверь 0. Всё в точных дробях.
"""
from fractions import Fraction as F
from itertools import product


def value(pr, g1, g0, tested):
    n, X = len(pr), range(len(g1))
    tot = F(0)
    for res in product(X, repeat=len(tested)):
        js = []
        for c in range(n):
            w = pr[c]
            for d, x in zip(tested, res):
                w *= g1[x] if d == c else g0[x]
            js.append(w)
        tot += max(js)
    return tot


def gain(pr, g1, g0, others):
    return value(pr, g1, g0, [0] + others) - value(pr, g1, g0, others)


def predicted_zero(pr, g1, g0, others):
    """Нуль ⇔ ни один атом M = max_{j≠0} p_j l_j не лежит строго в (p0·min l, p0·max l)."""
    L = [a / b for a, b in zip(g1, g0)]
    lo, hi = pr[0] * min(L), pr[0] * max(L)
    n, atoms = len(pr), set()
    for res in product(range(len(g1)), repeat=len(others)):
        prob = F(1)
        for x in res:
            prob *= g0[x]
        if prob == 0:
            continue
        lv = {d: L[x] for d, x in zip(others, res)}
        atoms.add(max(pr[j] * lv.get(j, 1) for j in range(1, n)))
    return not any(lo < s < hi for s in atoms)


if __name__ == "__main__":
    tests = [((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4))),                 # бинарный, h=3, l=1/3
             ((F(1), F(0)), (F(1, 2), F(1, 2))),                       # Монти-монетка q=1/2
             ((F(1, 5), F(2, 5), F(2, 5)), (F(2, 5), F(2, 5), F(1, 5))),  # трёхзначный (контрпример P1)
             ((F(1, 2), F(1, 3), F(1, 6)), (F(1, 6), F(1, 3), F(1, 2)))]
    priors = [[F(1, 3)] * 3, [F(1, 2), F(1, 4), F(1, 4)], [F(1, 10), F(9, 20), F(9, 20)],
              [F(1, 30), F(29, 60), F(29, 60)], [F(1, 5), F(1, 2), F(3, 10)], [F(3, 5), F(1, 10), F(3, 10)],
              [F(1, 4)] * 4, [F(2, 5), F(1, 5), F(1, 5), F(1, 5)], [F(1, 10), F(3, 10), F(3, 10), F(3, 10)]]
    n_ok = zeros = 0
    for g1, g0 in tests:
        for pr in priors:
            n = len(pr)
            for others in (list(range(1, n)), list(range(1, n - 1))):
                g = gain(pr, list(g1), list(g0), others)
                assert g >= 0
                assert (g == 0) == predicted_zero(pr, list(g1), list(g0), others), (g1, pr, others, g)
                n_ok += 1
                zeros += g == 0
    print(f"P13: критерий нуля совпал в {n_ok} случаях (нулей {zeros}).")

    # Бинарный шумный тест: нули ровно при r<=l/h, r=1, r>=h/l (r=p0/p, остальные проверены).
    a, b = F(3, 4), F(1, 4)
    for n in (3, 4):
        for r in (F(1, 20), F(1, 9), F(1, 8), F(1, 2), F(1), F(2), F(8), F(9), F(20)):
            p = 1 / (n - 1 + r)
            g = gain([r * p] + [p] * (n - 1), [a, 1 - a], [b, 1 - b], list(range(1, n)))
            assert (g == 0) == (r <= F(1, 9) or r == 1 or r >= 9)
    # Готовый пример: n=3, тест 3/4 против 1/4.
    ex = {r: gain([r / (2 + r), 1 / (2 + r), 1 / (2 + r)], [a, 1 - a], [b, 1 - b], [1, 2]) for r in (F(1, 2), F(1), F(2))}
    assert ex == {F(1, 2): F(9, 320), F(1): 0, F(2): F(21, 256)}
    print("Бинарный тест 3/4|1/4: ноль только при r<=1/9, r=1, r>=9; пример r=1/2, 1, 2:", ex[F(1, 2)], ex[F(1)], ex[F(2)])
    # Замкнутая формула из шести кусков (P13, п. 4).
    def closed(n, a, b, r):
        h, l, Q, p = a / b, (1 - a) / (1 - b), (1 - b) ** (n - 1), 1 / (n - 1 + r)
        if r <= l / h:
            return F(0)
        if r <= l:
            return Q * p * b * (r * h - l)
        if r <= 1:
            return Q * p * (1 - a) * (1 - r)
        if r <= h:
            return (1 - Q) * p * a * (r - 1)
        if r <= h / l:
            return (1 - Q) * p * (1 - b) * (h - r * l)
        return F(0)
    k = 0
    for a, b in ((F(3, 4), F(1, 4)), (F(2, 3), F(1, 5)), (F(9, 10), F(1, 2)), (F(3, 5), F(2, 5))):
        for n in (3, 4):
            for r in [F(j, 8) for j in range(1, 100)]:
                p = 1 / (n - 1 + r)
                assert gain([r * p] + [p] * (n - 1), [a, 1 - a], [b, 1 - b], list(range(1, n))) == closed(n, a, b, r)
                k += 1
    print(f"Формула из шести кусков: {k} точных совпадений.")
    # Зеркало R02 при неравных априорах (P13, п. 6).
    def both(pr, g1, g0, tested, g):
        fv = ov = F(0)
        for res in product(range(len(g1)), repeat=len(tested)):
            js = []
            for c in range(len(pr)):
                w = pr[c]
                for d, x in zip(tested, res):
                    w *= g1[x] if d == c else g0[x]
                js.append(w)
            fv += max(js)
            ov += max(0, max((1 + g) * j - g * sum(js) for j in js))
        return fv, ov
    pr, t1, t0 = [F(1, 5), F(2, 5), F(2, 5)], [F(2, 3), F(1, 3)], [F(1, 3), F(2, 3)]
    f1, o1 = both(pr, t1, t0, [0, 1, 2], F(1))
    f0, o0 = both(pr, t1, t0, [1, 2], F(1))
    assert (f1 - f0, o1 - o0, o0) == (F(4, 135), 0, F(8, 45))
    print("Зеркало R02: обязательный выбор +4/135, право уйти +0 при выигрыше 8/45.")
    print("ALL OK")
