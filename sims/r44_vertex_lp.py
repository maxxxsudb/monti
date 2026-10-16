"""Точная редукция: V* = ЛП по вершинным апостериорам (расщепление Kamenica–Gentzkow + выпуклость TV).

Для каждого S (|S|>=2) допустимые истинные апостериоры P: носитель в S, сумма 1, P<=c,
P_top - P_t >= dT (top — вершина π на S). Цель TV(P, наивное_S) выпукла по P, поэтому
достаточно вершин многогранника. Задача: max sum w_v·TV_v при sum w_v·P_v = π, w>=0 — ЛП.
ЛП разрешает одному S нести несколько апостериоров (сообщение = S + метка, которую наивный игнорирует);
это точное значение модели «с метками». Модель «только множества» (MILP r43) не больше ЛП.
Двойственная ЛП — сертификат оптимальности модели с метками.
"""
import itertools
import numpy as np
from scipy.optimize import linprog


def vertices(pi, S, c, dT):
    S = list(S); k = len(S)
    best_prior = max(pi[t] for t in S)
    tops = [i for i, t in enumerate(S) if abs(pi[t] - best_prior) < 1e-12]
    rows, rhs = [], []                      # неравенства G p <= h
    for i in range(k):
        e = np.zeros(k); e[i] = -1; rows.append(e); rhs.append(0)       # p >= 0
        e = np.zeros(k); e[i] = 1; rows.append(e); rhs.append(c)        # p <= c
        for it in tops:
            if i != it:
                e = np.zeros(k); e[i] = 1; e[it] = -1; rows.append(e); rhs.append(-dT)  # every naive maximizer must remain optimal
    G = np.array(rows); h = np.array(rhs); out = []
    for act in itertools.combinations(range(len(G)), k - 1):
        A = np.vstack([np.ones(k), G[list(act)]]); b = np.concatenate([[1], h[list(act)]])
        if abs(np.linalg.det(A)) < 1e-12:
            continue
        p = np.linalg.solve(A, b)
        if np.all(G @ p <= h + 1e-9):
            if not any(np.allclose(p, q) for q in out):
                out.append(p)
    return [(S, p) for p in out]


def solve_lp(pi, c=1.0, dT=0.0, dN=0.0):
    n = len(pi); pi = np.array(pi, float); cand = []
    for k in range(2, n + 1):
        for S in itertools.combinations(range(n), k):
            q = sorted(pi[list(S)] / pi[list(S)].sum(), reverse=True)
            if q[0] - q[1] < dN - 1e-12:
                continue
            for S_, p in vertices(pi, S, c, dT):
                naive = pi[S_] / pi[S_].sum()
                full = np.zeros(n); full[S_] = p
                cand.append((S_, full, 0.5 * np.abs(p - naive).sum()))
    if c >= 1:                               # одиночные сообщения допустимы только без потолка
        for t in range(n):
            full = np.zeros(n); full[t] = 1; cand.append(([t], full, 0.0))
    if not cand:
        return None
    A = np.array([cd[1] for cd in cand]).T; obj = -np.array([cd[2] for cd in cand])
    res = linprog(obj, A_eq=A, b_eq=pi, bounds=(0, None), method="highs")
    if res.status != 0:
        return None
    return -res.fun, res.eqlin.marginals     # двойственные переменные — сертификат


if __name__ == "__main__":
    import sys; sys.path.insert(0, "sims")
    from r43_naive_cap import solve_cap
    cases = [([0.39, 0.28, 0.2, 0.13], 0.5, 0.1), ([0.5, 0.3, 0.12, 0.08], 0.5, 0.2),
             ([0.5, 0.3, 0.2], 0.5, 0.0), ([0.4, 0.3, 0.2, 0.1], 0.75, 0.0), ([0.45, 0.3, 0.15, 0.1], 0.6, 0.05)]
    for pi, c, d in cases:
        lp = solve_lp(pi, c=c, dT=d, dN=d)[0]
        mi = solve_cap(pi, c=c, delta=d, dT=d)[0]
        assert lp >= mi - 1e-7, (pi, c, d, lp, mi)
        print(f"pi={pi} c={c} δ={d}: с метками (ЛП) {lp:.6f} >= только множества (MILP) {mi:.6f}")
    print("ALL OK")
