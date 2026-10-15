"""Парадокс последнего экзамена: точный перебор + Монте-Карло.
N кандидатов, ровно один эксперт (равномерно). Эксперт проходит тест всегда,
неэксперт проходит с вероятностью 1-f. Тестируем k первых кандидатов,
затем выбираем Байес-оптимально. Точность = P(выбран эксперт)."""
import itertools, random
from fractions import Fraction as F

def exact(N, k, f):
    acc = Fraction0 = F(0)
    # перебор результатов тестов k кандидатов
    for res in itertools.product([0, 1], repeat=k):
        w = []
        for e in range(N):
            p = F(1, N)
            for i, r in enumerate(res):
                pp = 1 if i == e else 1 - f
                p *= pp if r else 1 - pp
            w.append(p)
        acc += max(w)
    return acc

def mc(N, k, f, T=400000, rng=random.Random(1)):
    win = 0
    for _ in range(T):
        e = rng.randrange(N)
        res = [1 if (i == e or rng.random() < 1 - f) else 0 for i in range(k)]
        passed = [i for i in range(k) if res[i]]
        if passed:
            pick = rng.choice(passed)          # прошедший тест лучше непроверенного
        else:
            pick = rng.randrange(k, N) if k < N else rng.randrange(N)
        win += pick == e
    return win / T

for N, f in [(2, F(1, 2)), (3, F(1, 2)), (4, F(1, 3)), (5, F(3, 4))]:
    row = []
    for k in range(N + 1):
        ex = exact(N, k, f)
        formula = sum(f**j for j in range(min(k, N - 1) + 1)) / N
        assert ex == formula, (N, k, f, ex, formula)
        row.append(f"k={k}: {str(ex):>7} ({float(ex):.4f}, MC {mc(N, k, float(f)):.4f})")
    print(f"N={N} f={f}:", " | ".join(row))
print("Формула (1/N)*sum_{j<=min(k,N-1)} f^j подтверждена точно; последний тест даёт 0.")
