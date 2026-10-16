"""Рента знания протокола против ценности решения (предварительная фиксация, облачный Claude).

Монетка Монти q, N=3, защита-вычёркивание. Контракт «машина за вашей дверью 0» платит 1.
Наивный рынок (CAR) ставит цену p_0/(сумма априоров закрытых дверей). Информированный ставщик
берёт выгодную сторону единичной ставки: рента R0 = sum_m P(m) |P_true(0|m) - P_naive(0|m)|.
"""
from fractions import Fraction as F
from itertools import product


def messages(pr, q, protect=True):
    N = len(pr)
    out = {}
    for c in range(N):
        goats = [d for d in range(N) if d != c and not (protect and d == 0)]
        for bits in product([0, 1], repeat=len(goats)):
            w = pr[c]
            opened = set()
            for g, b in zip(goats, bits):
                w *= q if b else 1 - q
                if b:
                    opened.add(g)
            v = out.setdefault(frozenset(opened), [F(0)] * N)
            v[c] += w
    return out


def rent0(pr, q):
    tot = F(0)
    for o, v in messages(pr, q).items():
        Pm = sum(v)
        closed = [d for d in range(len(pr)) if d not in o]
        naive = pr[0] / sum(pr[d] for d in closed)
        tot += Pm * abs(v[0] / Pm - naive)
    return tot


def decision_value_gap(pr, q):
    """Ценность для выбирающего: выигрыш без защиты минус с защитой (P12)."""
    def best(out):
        return sum(max(v[d] for d in range(len(pr)) if d not in o) for o, v in out.items())
    return best(messages(pr, q, protect=False)) - best(messages(pr, q, protect=True))


if __name__ == "__main__":
    eq = [F(1, 3)] * 3
    for q in (F(1, 4), F(1, 2), F(3, 4)):
        assert rent0(eq, q) == q * (q + 2) / 9
        assert decision_value_gap(eq, q) == 0
    print("Равные априоры: ценность защиты для выбирающего 0 (R01), рента знания протокола q(q+2)/9 > 0.")
    print("ALL OK")
