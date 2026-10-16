"""P16: потеря от вычёркивания для любого перестановочного ведущего; монетка — худший ведущий.

Формула потерь при законе размера плана w (P16), безпотерьность при отсутствии соседних размеров,
максимум по w при равных соперниках — монетка q=1-p/p0, значение (p0-p)(1-q^{N-1}).
"""
import random
from fractions import Fraction as F
from math import comb

from r10_deletion import exch, protected, subsets, win


def loss_formula(N, w, pr):
    A = lambda m: w[m] / comb(N - 1, m) if 0 <= m <= N - 1 else 0
    return sum(max(0, min(max(pr[d] for d in C) * A(N - len(C)), (pr[0] - max(pr[d] for d in C)) * A(N - 1 - len(C))))
               for C in subsets(range(1, N)) if C)


if __name__ == "__main__":
    R = random.Random(16)
    n = 0
    for N in (3, 4, 5):
        for _ in range(60):
            w = [R.randint(0, 5) for _ in range(N)]
            if sum(w) == 0:
                continue
            w = [F(x, sum(w)) for x in w]
            v = [R.randint(1, 9) for _ in range(N)]
            pr = [F(x, sum(v)) for x in v]
            assert win(N, pr, exch(N, w)) - protected(N, pr, exch(N, w)) == loss_formula(N, w, pr)
            # без соседних размеров потеря нулевая при любых априорах
            if all(w[m] * w[m + 1] == 0 for m in range(N - 1)):
                assert loss_formula(N, w, pr) == 0
            n += 1
    print(f"Формула потерь для перестановочного ведущего: {n} точных совпадений.")

    # Ключевое неравенство: b_n * P(M<=k) <= b_k для M~Bin(n,q), k<n.
    for n_ in range(1, 12):
        for q in [F(j, 13) for j in range(1, 13)]:
            b = [comb(n_, i) * q**i * (1 - q) ** (n_ - i) for i in range(n_ + 1)]
            for k in range(n_):
                assert b[n_] * sum(b[: k + 1]) <= b[k]
    # Монетка — максимум: случайные законы w не превосходят (p0-p)(1-q^{N-1}).
    m = 0
    for N in (3, 4, 5, 6):
        for p0 in [F(j, 20) for j in range(1, 20)]:
            p = (1 - p0) / (N - 1)
            if p0 <= p:
                continue
            q = 1 - p / p0
            best = (p0 - p) * (1 - q ** (N - 1))
            wc = [comb(N - 1, k) * q**k * (1 - q) ** (N - 1 - k) for k in range(N)]
            assert loss_formula(N, wc, [p0] + [p] * (N - 1)) == best
            for _ in range(40):
                w = [F(R.randint(0, 9)) for _ in range(N)]
                if sum(w) == 0:
                    continue
                w = [x / sum(w) for x in w]
                assert loss_formula(N, w, [p0] + [p] * (N - 1)) <= best
                m += 1
    print(f"Монетка — худший перестановочный ведущий: {m} случайных законов не превзошли (p0-p)(1-q^(N-1)).")
    print("ALL OK")
