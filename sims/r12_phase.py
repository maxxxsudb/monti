"""P15: монетка — зеркала R02 не бывает; фазовые классы «обязательный выбор / право уйти».

Ведущий с монеткой q: тест двери «закрыта» (у машины всегда, у козы 1-q) / «открыта» (у козы q).
Проверка двери 0 = снятие запрета. Выплаты: машина +1, коза -g, уход 0. Точные дроби.
"""
from fractions import Fraction as F
from itertools import product


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


if __name__ == "__main__":
    classes = {}
    priors = {3: [[F(a, 12), F(b, 12), F(12 - a - b, 12)] for a in range(1, 11) for b in range(1, 12 - a)],
              4: [[F(a, 10), F(b, 10), F(c, 10), F(10 - a - b - c, 10)]
                  for a in (1, 3, 5, 7) for b in (1, 2) for c in (1, 2) if 10 - a - b - c > 0]}
    for N, prs in priors.items():
        for q in (F(1, 4), F(1, 2), F(3, 4)):
            g1, g0 = [F(1), F(0)], [1 - q, q]
            for pr in prs:
                for g in (F(1, 2), F(1), F(2), F(4)):
                    f1, o1 = both(pr, g1, g0, list(range(N)), g)
                    f0, o0 = both(pr, g1, g0, list(range(1, N)), g)
                    k = ("F+" if f1 > f0 else "F0") + ("O+" if o1 > o0 else "O0")
                    classes[k] = classes.get(k, 0) + 1
                    assert k != "F+O0", (N, q, pr, g)            # теорема P15
                    assert (f1 > f0) == (pr[0] > min(x for x in pr[1:] if x > 0))  # P12: обязательный выбор
    print("Монетка, N=3,4, неравные априоры, штраф 1/2..4: классы", classes, "— F+O0 (зеркало) не встречается.")
    # Обобщение: любой тест с исходом-исключением (g1=0 при g0>0), все соперники проверены.
    ex = {}
    for g1, g0, pr in [(a, b, pr) for a, b in (([F(1, 2), F(1, 2), F(0)], [F(1, 4), F(1, 4), F(1, 2)]),
                                                 ([F(2, 3), F(1, 3), F(0)], [F(1, 3), F(1, 3), F(1, 3)]))
                       for pr in priors[3]]:
        for g in (F(1, 2), F(1), F(2), F(4)):
            f1, o1 = both(pr, g1, g0, [0, 1, 2], g)
            f0, o0 = both(pr, g1, g0, [1, 2], g)
            k = ("F+" if f1 > f0 else "F0") + ("O+" if o1 > o0 else "O0")
            ex[k] = ex.get(k, 0) + 1
            assert k != "F+O0", (pr, g)
    print("Тесты с исключением (l={2,0} и l={2,1,0}): классы", ex, "— зеркала нет.")
    print("ALL OK")
