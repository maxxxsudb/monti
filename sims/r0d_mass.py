# r0d_mass.py -- критерий сохранения массы A/k = B/(N-k): точный перебор + Монте-Карло
import random, itertools
from fractions import Fraction as Fr
from math import comb
random.seed(1)
T = 10**6

def exact_post(N, Y, kernel, s):
    """kernel(i) -> dict{frozenset s: prob}; возвращает P(tau in Y | S=s), A/k, B/(N-k)"""
    K = {i: kernel(i).get(s, Fr(0)) for i in range(1, N+1)}
    A = sum(K[i] for i in Y); B = sum(K[j] for j in K if j not in Y)
    k = len(Y)
    if A + B == 0: return None
    return A/(A+B), A/k, B/(N-k)

# --- 1) Симметричный target-preserving: N=100,k=20,m=5 (MC) ---
N, k, m = 100, 20, 5
O = list(range(k+1, N+1))
hitY = 0; hit_j = 0; pair_j = 0; pair_y = 0
for _ in range(T):
    tau = random.randint(1, N)
    if tau <= k:
        s = random.sample(O, m)
    else:
        rest = [x for x in random.sample(O, m) if x != tau][:m-1]
        s = [tau] + rest
        random.shuffle(s)
    hitY += tau <= k
    # конкретный survivor = первый в s (случайный из m)
    if tau == s[0]: hit_j += 1
    if tau == s[0]: pair_j += 1
    if tau == 1: pair_y += 1
print("1) N=100 k=20 m=5 symmetric target-preserving")
print("   P(Y)  exact %.4f  MC %.4f" % (k/N, hitY/T))
print("   p_j   exact %.4f  MC %.4f" % ((N-k)/(N*m), hit_j/T))
print("   pairwise P(j | tau in {j,y}) exact %.4f MC %.4f  (C=%g)" % (16/17, pair_j/(pair_j+pair_y), (N-k)/m))

# --- 2) Обменный, но НЕ target-preserving (Monty Fall): N=3,k=1,m=1 ---
acc = 0; win = 0
for _ in range(T):
    tau = random.randint(1, 3)
    opened = random.choice([2, 3])
    if opened == tau: continue
    acc += 1; win += (tau == 1)
print("2) Monty Fall (exchangeable, NOT target-preserving): P(Y|goat shown) exact 0.5000  MC %.4f  accepted %d" % (win/acc, acc))
# точно: K_1({2}) = 1/2 (открыл 3), K_2({2})=1/2, K_3({2})=0 -> A/k=1/2, B/2=1/4
print("   A/k=1/2, B/(N-k)=1/4 -> criterion violated although kernel is exchangeable")

# --- 3) Контрпример из 'сонет': N=4, Y={1}, m=2 ---
rule = {1: (2, 3), 2: (2, 3), 3: (2, 4), 4: (3, 4)}
print("3) sonnet counterexample: tau=3 -> {2,4} target-preserving?", 3 in rule[3])
acc = 0; win = 0; Ysum = 0
for _ in range(T):
    tau = random.randint(1, 4); s = rule[tau]
    Ysum += (tau == 1)
    if s == (2, 3):
        acc += 1; win += (tau == 1)
print("   P(Y|S={2,3}) exact 0.5000 MC %.4f (accepted %d); E over s of P(Y|s) = 1/4, MC P(Y) %.4f" % (win/acc, acc, Ysum/T))

# --- 3b) Чистый пример предпочтения БЕЗ выбрасывания цели (Monty Crawl-тип) ---
# N=4, Y={1}, m=2, если tau in Y ведущий всегда оставляет {2,3}; если tau=j in O -- оставляет {j, min другой}
def ker_pref(i):
    if i == 1: return {frozenset((2, 3)): Fr(1)}
    other = min(x for x in (2, 3, 4) if x != i)
    return {frozenset((i, other)): Fr(1)}
for s in [frozenset((2, 3)), frozenset((2, 4)), frozenset((3, 4))]:
    r = exact_post(4, [1], ker_pref, s)
    if r is None: print("3b) S=%s impossible" % sorted(s)); continue
    print("3b) preference, target-preserving: S=%s P(Y|s)=%s  A/k=%s B/(N-k)=%s" % (sorted(s), *r))

# --- 4) Точный перебор: симметричный протокол при всех s сохраняет k/N ---
def sym_kernel_factory(N, k, m):
    O = list(range(k+1, N+1)); subs = [frozenset(c) for c in itertools.combinations(O, m)]
    def ker(i):
        if i <= k: return {s: Fr(1, len(subs)) for s in subs}
        good = [s for s in subs if i in s]
        return {s: Fr(1, len(good)) for s in good}
    return ker, subs
for (N, k, m) in [(5, 2, 2), (7, 3, 2), (6, 1, 3)]:
    ker, subs = sym_kernel_factory(N, k, m)
    vals = {exact_post(N, list(range(1, k+1)), ker, s)[0] for s in subs}
    print("4) symmetric N=%d k=%d m=%d: P(Y|s) over all s = %s (k/N=%s)" % (N, k, m, vals, Fr(k, N)))

# --- 5) Следствие: один выживший против всей своей группы: survivor > group iff N-k > k*m ---
N, k, m = 10, 3, 2
O = list(range(k+1, N+1)); g = 0; sv = 0
for _ in range(T):
    tau = random.randint(1, N)
    if tau <= k: s = random.sample(O, m)
    else:
        s = [tau] + random.sample([x for x in O if x != tau], m-1); random.shuffle(s)
    g += tau <= k; sv += tau == s[0]
print("5) N=10 hold k=3, m=2 survivors: group exact %.4f MC %.4f; one survivor exact %.4f MC %.4f" % (k/N, g/T, (N-k)/(N*m), sv/T))
