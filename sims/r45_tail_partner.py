"""Конструкция «хвост + дальний партнёр» (модель с метками, c=1/2, запас знающего 0).

Сообщение: хвост S_j={j..n-1}, если наивный запас (Q_top - Q_second) >= dN; истина 1/2 на j и 1/2 на m>j.
ЛП по весам таких сообщений при sum w·P = π. Сверка с полной ЛП r44 и предел при больших n.
"""
import numpy as np
from scipy.optimize import linprog


def tail_lp(pi, dN):
    n = len(pi); cols, val = [], []
    for j in range(n):
        T = pi[j:].sum(); Q = pi[j:] / T
        if len(Q) < 2 or Q[0] - Q[1] < dN - 1e-12:
            continue
        for m in range(j + 1, n):
            P = np.zeros(n); P[j] = P[m] = 0.5
            tv = 0.5 * (np.abs(P[j:] - Q).sum())
            cols.append(P); val.append(tv)
    if not cols:
        return None
    res = linprog(-np.array(val), A_eq=np.array(cols).T, b_eq=pi, bounds=(0, None), method="highs")
    return -res.fun if res.status == 0 else None


def geo(n, rho):
    w = np.array([rho ** j for j in range(n)]); return w / w.sum()


if __name__ == "__main__":
    import sys; sys.path.insert(0, "sims")
    from r44_vertex_lp import solve_lp
    full = solve_lp(list(geo(6, 0.71)), c=0.5, dN=0.1)[0]
    tail = tail_lp(geo(6, 0.71), 0.1)
    print(f"n=6, ρ=0.71, δ_N=0.1: полная ЛП {full:.4f}, хвост+партнёр {tail}")
    for n in (6, 9, 15, 30, 60):
        best = max((tail_lp(geo(n, r / 1000), 0.1) or 0, r / 1000) for r in range(600, 700, 4))
        print(f"n={n}: лучшее хвост+партнёр {best[0]:.4f} при ρ={best[1]}")
