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


# ---------- Кто верит в 50/50: двойственность видимой и невидимой связи ----------
def tie_losses(pr, out):
    """(потеря при лучшем, случайном, худшем выборе среди наивно-лучших; средняя полная вариация)."""
    N = len(pr)
    lb = lr = lw = tv = F(0)
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
        lb += Pm * (mt - max(tr[d] for d in nav))
        lr += Pm * (mt - sum(tr[d] for d in nav) / len(nav))
        lw += Pm * (mt - min(tr[d] for d in nav))
        tv += Pm * sum(abs(tr[d] - nv[d]) for d in cl) / 2
    return lb, lr, lw, tv


if __name__ == "__main__":
    for N in range(3, 11):
        eq = [F(1, N)] * N
        half = [F(1, 2)] + [F(1, 2 * (N - 1))] * (N - 1)
        t = F(N - 2, 2 * N)
        assert tie_losses(eq, classic_msgs(eq, N - 2)) == (0, t, 2 * t, t)       # наивный 50/50: видимо
        assert tie_losses(half, classic_msgs(half, N - 2)) == (0, 0, 0, t)      # знающий 50/50: невидимо
    print("Двойственность 50/50: тот же сдвиг (N-2)/(2N); наивный 50/50 — потеря = сдвиг (наугад) или 2*сдвиг (упрямо); знающий 50/50 — потеря 0.")
    print("ALL OK")


# ---------- Честный ведущий-интересант: ставки только по публичному сообщению ----------
def two_closed_rent(N, rule):
    """Равные априоры; rule(car) -> [(закрытое множество из 2 дверей, вероятность)];
    наивная цена 1/2 на каждую закрытую. Возвращает среднюю полную вариацию = легальную ренту."""
    msgs = {}
    for c in range(N):
        for S, pr in rule(c):
            v = msgs.setdefault(frozenset(S), [F(0)] * N)
            v[c] += F(1, N) * pr
    return sum(sum(v) * sum(abs(v[d] / sum(v) - F(1, 2)) for d in S) / 2 for S, v in msgs.items())


if __name__ == "__main__":
    import random
    R = random.Random(7)
    for N in range(3, 8):
        for _ in range(20):
            w = [F(R.randint(0, 9)) for _ in range(N - 1)]
            if sum(w) == 0:
                w[0] = F(1)
            w = [x / sum(w) for x in w]
            prot = lambda c, w=w: [({0, d}, w[d - 1]) for d in range(1, N)] if c == 0 else [({0, c}, F(1))]
            assert two_closed_rent(N, prot) == F(N - 2, 2 * N)          # под запретом: инвариант
        assert two_closed_rent(N, lambda c: [({c, (c + 1) % N}, F(1))]) == F(1, 2)   # без запрета: кодирование
    print("Честный ведущий: под запретом рента (N-2)/(2N) при любом предпочтении; без запрета кодирование даёт 1/2.")
    print("ALL OK")


# ---------- Влияние на ведущего: равномерный — минимум ренты; частичное сотрудничество выпукло ----------
def protected_rent(N, prefs):
    msgs = {}
    for c in range(N):
        for S, pr in prefs[c].items():
            v = msgs.setdefault(S, [F(0)] * N)
            v[c] += pr * F(1, N)
    return sum(sum(v) * sum(abs(v[d] / sum(v) - F(1, len(S))) for d in S) / 2 for S, v in msgs.items() if sum(v) > 0)


def protected_options(N, k, c):
    rv = list(range(1, N))
    if c == 0:
        return [frozenset((0,) + T) for T in combinations(rv, k - 1)]
    return [frozenset((0, c) + T) for T in combinations([d for d in rv if d != c], k - 2)]


if __name__ == "__main__":
    import random
    R = random.Random(11)
    for N, k in ((4, 3), (5, 3), (5, 4)):
        opts = [protected_options(N, k, c) for c in range(N)]
        uni = [{S: F(1, len(o)) for S in o} for o in opts]
        r_uni = protected_rent(N, uni)
        for _ in range(40):
            prefs = []
            for o in opts:
                w = [F(R.randint(0, 6)) for _ in o]
                if sum(w) == 0:
                    w[0] = F(1)
                prefs.append({S: x / sum(w) for S, x in zip(o, w)})
            assert protected_rent(N, prefs) >= r_uni          # равномерный ведущий — минимум
    # код (N=5, k=3): машина c -> {0, c, следующая по кругу}; машина у вас -> {0, 1, 3}
    code = [{frozenset((0, 1, 3)): F(1)}] + [{frozenset((0, c, c % 4 + 1)): F(1)} for c in range(1, 5)]
    uni5 = [{S: F(1, len(o)) for S in o} for o in (protected_options(5, 3, c) for c in range(5))]
    half = [{S: uni5[c].get(S, F(0)) / 2 + code[c].get(S, F(0)) / 2 for S in set(uni5[c]) | set(code[c])} for c in range(5)]
    assert (protected_rent(5, uni5), protected_rent(5, code), protected_rent(5, half)) == (F(2, 15), F(2, 3), F(16, 45))
    print("Влияние на ведущего: равномерный — минимум; код до 2/3; половина сотрудничества 16/45 < линейной 2/5.")
    print("ALL OK")
