"""Убеждение наивного получателя с потолком уверенности c (ответ не выдаётся) и запасом наивного δ.

Без лазейки r42: бюджеты — РАВЕНСТВА sum_S x[S,θ] = π_θ по всем сообщениям, включая одиночные;
потолок x[S,θ] <= c·x(S) действует на все сообщения (одиночное при c<1 автоматически запрещено).
Решения не меняются: вершина π на S (все вершины при ничьей) истинно лучшая.
Запас наивного: сообщение S допустимо, только если наивная вероятность вершины минус вторая >= δ.
Цель: max E·TV(истинное, наивное). scipy.optimize.milp; результат принимается только при status==0.
"""
import itertools
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def solve_cap(pi, c=1.0, delta=0.0):
    n = len(pi)
    pi = np.array(pi, float)
    msgs = []
    for k in range(1, n + 1):
        for S in itertools.combinations(range(n), k):
            q = sorted((pi[list(S)] / pi[list(S)].sum()), reverse=True)
            if k == 1 or q[0] - q[1] >= delta - 1e-12:
                msgs.append(S)
    idx = {}
    for kind in ("x", "u", "z"):
        for S in msgs:
            for t in S:
                idx[(kind, S, t)] = len(idx)
    nv = len(idx)
    obj = np.zeros(nv); integ = np.zeros(nv)
    for S in msgs:
        for t in S:
            obj[idx[("u", S, t)]] = -1
            integ[idx[("z", S, t)]] = 1
    A, lo, hi = [], [], []

    def add(row, l, h):
        A.append(row); lo.append(l); hi.append(h)
    for th in range(n):                       # бюджет — равенство
        row = np.zeros(nv)
        for S in msgs:
            if th in S:
                row[idx[("x", S, th)]] = 1
        add(row, pi[th], pi[th])
    for S in msgs:
        piS = pi[list(S)].sum()
        top = max(pi[t] for t in S)
        tops = [t for t in S if abs(pi[t] - top) < 1e-12]
        for m in tops:                        # решение не меняется
            for t in S:
                if t != m:
                    row = np.zeros(nv); row[idx[("x", S, m)]] = 1; row[idx[("x", S, t)]] = -1
                    add(row, 0, np.inf)
        for t in S:                           # потолок уверенности
            row = np.zeros(nv)
            for s2 in S:
                row[idx[("x", S, s2)]] -= c
            row[idx[("x", S, t)]] += 1
            add(row, -np.inf, 0)
            # положительная часть наивная - истинная
            row = np.zeros(nv); row[idx[("u", S, t)]] = 1
            for s2 in S:
                row[idx[("x", S, s2)]] -= pi[t] / piS
            row[idx[("x", S, t)]] += 1; row[idx[("z", S, t)]] += 1
            add(row, -np.inf, 1)
            row = np.zeros(nv); row[idx[("u", S, t)]] = 1; row[idx[("z", S, t)]] = -1
            add(row, -np.inf, 0)
    res = milp(obj, constraints=LinearConstraint(np.array(A), lo, hi), integrality=integ,
               bounds=Bounds(np.zeros(nv), np.ones(nv)), options={"time_limit": 120})
    if res.status != 0 or res.x is None:
        return None, None
    x = {S: {t: res.x[idx[("x", S, t)]] for t in S} for S in msgs}
    return -res.fun, x


if __name__ == "__main__":
    # без потолка совпадает с r42 (n=2: a(1-a)); с потолком c<1 при n=2 сдвига нет вовсе
    for a in (0.6, 0.75, 0.9):
        v, _ = solve_cap([a, 1 - a], c=1.0)
        assert abs(v - a * (1 - a)) < 1e-7
        v, _ = solve_cap([a, 1 - a], c=0.99)
        assert v is not None and abs(v) < 1e-7
    print("n=2: без потолка a(1-a); при любом c<1 сдвиг 0 (вся масса в {1,2}, истина = априор).")
    for pi in ([0.5, 0.3, 0.2], [0.45, 0.35, 0.2], [0.4, 0.3, 0.2, 0.1]):
        row = []
        for c in (1.0, 0.9, 0.75, 0.6, 0.5):
            v, _ = solve_cap(pi, c=c)
            row.append((c, None if v is None else round(v, 5)))
        print("pi", pi, "V*(c):", row)
