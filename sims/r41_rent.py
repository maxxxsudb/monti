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


# ---------- Невидимая рента: решения наивных не меняются, цены сдвинуты ----------
from itertools import combinations


def classic_msgs(pr, k):
    """Квота k с перепланированием: ведущий открывает k коз среди чужих дверей равновероятно."""
    N = len(pr)
    out = {}
    for c in range(N):
        goats = [d for d in range(1, N) if d != c]
        subs = list(combinations(goats, k))
        for S in subs:
            v = out.setdefault(frozenset(S), [F(0)] * N)
            v[c] += pr[c] / len(subs)
    return out


def stealth(pr, out):
    """(потеря наивного выбирающего при худшем выборе среди наивно-лучших, средняя полная вариация, невидимость)."""
    N = len(pr)
    loss = tv = F(0)
    invisible = True
    for o, v in out.items():
        Pm = sum(v)
        if Pm == 0:
            continue
        cl = [d for d in range(N) if d not in o]
        tr = {d: v[d] / Pm for d in cl}
        S = sum(pr[d] for d in cl)
        nv = {d: pr[d] / S for d in cl}
        mt, mn = max(tr.values()), max(nv.values())
        nav = [d for d in cl if nv[d] == mn]
        invisible &= all(tr[d] == mt for d in nav)
        loss += Pm * (mt - min(tr[d] for d in nav))
        tv += Pm * sum(abs(tr[d] - nv[d]) for d in cl) / 2
    return loss, tv, invisible


if __name__ == "__main__":
    for N in range(3, 8):
        pr = [F(1, 2)] + [F(1, 2 * (N - 1))] * (N - 1)
        assert stealth(pr, classic_msgs(pr, N - 2)) == (0, F(N - 2, 2 * N), True)
    for N in (3, 4, 5):
        p0 = F(1, N) - F(1, 1000)
        pr = [p0] + [(1 - p0) / (N - 1)] * (N - 1)
        loss, tv, inv = stealth(pr, messages(pr, F(999, 1000)))
        assert loss == 0 and inv and F(N - 1, 2 * N) - F(1, 50) < tv < F(N - 1, 2 * N)
    # видимая полоса: равные априоры, классика — наивный теряет 1/3 = 2 * TV
    eq = [F(1, 3)] * 3
    assert stealth(eq, classic_msgs(eq, 1)) == (F(1, 3), F(1, 6), False)
    print("Невидимая рента: классика «все, кроме одной» (N-2)/(2N) при нулевой потере наивных; монетка -> (N-1)/(2N).")
    print("ALL OK")
