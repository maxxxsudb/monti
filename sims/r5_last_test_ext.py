"""Обобщения K-5: точная оптимальная точность при k тестах.
a = P(эксперт проходит), b = P(неэксперт проходит), E экспертов среди N (равномерно), надо выбрать одного эксперта."""
import itertools
from fractions import Fraction as F

def acc(N, k, a, b, E=1):
    experts_sets = list(itertools.combinations(range(N), E))
    pr = F(1, len(experts_sets))
    tot = F(0)
    for res in itertools.product([0, 1], repeat=k):
        # P(i эксперт, res) для каждого i
        score = [F(0)] * N
        for S in experts_sets:
            p = pr
            for i, r in enumerate(res):
                q = a if i in S else b
                p *= q if r else 1 - q
            for i in S:
                score[i] += p
        tot += max(score)
    return tot

def row(N, a, b, E=1):
    v = [acc(N, k, a, b, E) for k in range(N + 1)]
    return " ".join(f"{float(x):.4f}" for x in v), v[N] - v[N - 1]

h = F(1, 2)
print("один эксперт, ошибка только у неэкспертов (K-5):", row(3, F(1), h))
print("двусторонняя ошибка a=0.9,b=0.5:", row(3, F(9, 10), h))
print("двусторонняя ошибка a=0.99,b=0.5:", row(3, F(99, 100), h))
print("два эксперта из 4, a=1,b=1/2:", row(4, F(1), h, E=2))
print("один эксперт N=4, a=1, b=1/3:", row(4, F(1), F(1, 3)))
