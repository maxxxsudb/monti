"""K1, раунд 5: где «последний тест = 0» ЛОМАЕТСЯ. Точный перебор (Fraction) + MC-контроль ключевого случая.
Модель: миры S (множество экспертов) с априором; тестируем подмножество T; P(pass|эксперт)=a, P(pass|не)=b.
Ценность = Σ_исходы max_действие Σ_S P(S)P(исход|S)U(действие,S)."""
import itertools, math, random
from fractions import Fraction as F

def value(worlds, T, a, b, actions, U):
    tot = F(0)
    for res in itertools.product([0, 1], repeat=len(T)):
        best = None
        for act in actions:
            s = F(0)
            for S, p in worlds:
                q = p
                for i, r in zip(T, res):
                    pi = a if i in S else b
                    q *= pi if r else 1 - pi
                s += q * U(act, S)
            best = s if best is None or s > best else best
        tot += best
    return tot

def best_subset(N, k, worlds, a, b, actions, U):
    return max((value(worlds, T, a, b, actions, U), T) for T in itertools.combinations(range(N), k))

def one_expert(pri):
    return [(frozenset([i]), p) for i, p in enumerate(pri)]

def report(name, N, worlds, a, b, actions, U):
    vals = [best_subset(N, k, worlds, a, b, actions, U) for k in range(N + 1)]
    s = " ".join(f"{float(v):.4f}" for v, _ in vals)
    d = vals[N][0] - vals[N - 1][0]
    print(f"{name}\n   k=0..N: {s} | лучший T(N-1)={vals[N-1][1]} | ценность последнего = {d} ({float(d):.4f})")
    return d

hire = lambda act, S: 1 if act in S else 0
print("=== 0. Контроль K-5 (равные априоры, a=1, b=1/2, N=3) ===")
report("hire-one", 3, one_expert([F(1, 3)] * 3), F(1), F(1, 2), range(3), hire)

print("\n=== 1. Неравные априоры ===")
report("a=1, b=1/2, prior .5/.3/.2", 3, one_expert([F(5, 10), F(3, 10), F(2, 10)]), F(1), F(1, 2), range(3), hire)
d1 = report("a=4/5, b=1/2, prior 1/2,1/4,1/4", 3, one_expert([F(1, 2), F(1, 4), F(1, 4)]), F(4, 5), F(1, 2), range(3), hire)
report("a=4/5, b=1/5, prior 1/2,1/4,1/4", 3, one_expert([F(1, 2), F(1, 4), F(1, 4)]), F(4, 5), F(1, 5), range(3), hire)
# поиск максимума ценности последнего теста при неравных априорах (сетка)
best = (0, None)
for a_ in [F(i, 10) for i in range(5, 11)]:
    for b_ in [F(i, 10) for i in range(0, 10)]:
        if b_ >= a_: continue
        for p1 in [F(i, 20) for i in range(7, 19)]:
            rest = 1 - p1
            for p2n in range(1, 10):
                p2 = rest * F(p2n, 10); p3 = rest - p2
                if p3 <= 0 or p2 > p1 or p3 > p2: continue
                w = one_expert([p1, p2, p3])
                v2 = best_subset(3, 2, w, a_, b_, range(3), hire)[0]
                v3 = value(w, (0, 1, 2), a_, b_, range(3), hire)
                if v3 - v2 > best[0]: best = (v3 - v2, (a_, b_, p1, p2, p3, v2, v3))
print("   max ценности последнего (сетка, N=3):", float(best[0]), [str(x) for x in best[1]])

print("\n=== 2. Другая функция потерь: лог-скор / Брайер апостериора (равные априоры, a=1,b=1/2,N=3) ===")
def proper(N, T, a, b, kind):
    w = one_expert([F(1, N)] * N); tot = 0.0
    for res in itertools.product([0, 1], repeat=len(T)):
        joint = []
        for S, p in w:
            q = p
            for i, r in zip(T, res):
                pi = a if i in S else b
                q *= pi if r else 1 - pi
            joint.append(q)
        z = sum(joint)
        if z == 0: continue
        post = [x / z for x in joint]
        for i, q in enumerate(joint):
            if q == 0: continue
            if kind == "log": sc = math.log2(float(post[i]))
            else: sc = -sum(float((post[j] - (1 if j == i else 0)) ** 2) for j in range(N))
            tot += float(q) * sc
    return tot
for kind in ("log", "brier"):
    v = [proper(3, tuple(range(k)), F(1), F(1, 2), kind) for k in range(4)]
    print(f"   {kind}: k=0..3:", " ".join(f"{x:.4f}" for x in v), f"| вклад последнего = {v[3]-v[2]:.4f}")

print("\n=== 3. Несколько экспертов, цель — найти ВСЕХ (2 из 4, нанять пару, успех если оба эксперты) ===")
w24 = [(frozenset(S), F(1, 6)) for S in itertools.combinations(range(4), 2)]
pairs = [frozenset(P) for P in itertools.combinations(range(4), 2)]
report("pick-pair a=1,b=1/2", 4, w24, F(1), F(1, 2), pairs, lambda act, S: 1 if act == S else 0)
report("pick-one (контроль K-5) a=1,b=1/2", 4, w24, F(1), F(1, 2), range(4), hire)
# 1 из 3, но нужно назвать эксперта И неэксперта? -> ранжирование; тут: «нанять 2 из 3, успех если эксперт среди них» = отсеять одного
report("1 из 3: уволить одного, успех если уволен НЕ эксперт", 3, one_expert([F(1, 3)] * 3), F(1), F(1, 2), range(3), lambda act, S: 0 if act in S else 1)

print("\n=== 4. Право отказа: +1 эксперт, -c неэксперт, 0 отказ (равные априоры, N=3) ===")
for a_, b_, c in [(F(1), F(1, 2), F(1)), (F(1), F(1, 2), F(2)), (F(9, 10), F(1, 2), F(1)), (F(1), F(1, 2), F(1, 2))]:
    acts = list(range(3)) + ["no"]
    U = lambda act, S, c=c: 0 if act == "no" else (1 if act in S else -c)
    report(f"a={a_}, b={b_}, c={c}", 3, one_expert([F(1, 3)] * 3), a_, b_, acts, U)

print("\n=== 5. Неизвестное число экспертов (каждый независимо эксперт с p=1/3), нанять одного, N=3 ===")
wI = []
for mask in range(8):
    S = frozenset(i for i in range(3) if mask >> i & 1)
    wI.append((S, F(1, 3) ** len(S) * F(2, 3) ** (3 - len(S))))
report("must hire, a=1,b=1/2", 3, wI, F(1), F(1, 2), range(3), hire)

# MC-контроль случая 1 (a=4/5,b=1/2, prior 1/2,1/4,1/4)
print("\n=== MC-контроль 1: a=.8, b=.5, prior .5/.25/.25, 10^6 ===")
random.seed(1); n = 10**6; pri = [.5, .25, .25]; a_, b_ = .8, .5
def post_pick(res, T):
    sc = []
    for i in range(3):
        l = pri[i]
        for j, r in zip(T, res):
            pj = a_ if j == i else b_
            l *= pj if r else 1 - pj
        sc.append(l)
    return max(range(3), key=lambda i: sc[i])
for T in [(1, 2), (0, 2), (0, 1), (0, 1, 2)]:
    ok = 0
    rnd = random.random
    for _ in range(n):
        u = rnd(); e = 0 if u < .5 else (1 if u < .75 else 2)
        res = tuple(1 if rnd() < (a_ if j == e else b_) else 0 for j in T)
        ok += post_pick(res, T) == e
    print(f"   T={T}: MC {ok/n:.4f}  exact {float(value(one_expert([F(1,2),F(1,4),F(1,4)]), T, F(4,5), F(1,2), range(3), hire)):.4f}")
