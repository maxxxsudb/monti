# r0d_timed.py -- КАНДИДАТ "Монти без ведущего, с часами":
# 3 ячейки, 2 бомбы, 1 пустая; ваша (№1) бомба заглушена амулетом. Незаглушённые бомбы взрываются сами
# в случайный момент со функцией выживания S(t) (одинаковое распределение, независимо).
# Наблюдение: первый взрыв -- в ячейке №3 в момент t. Точно: P(stay | t) = S(t) / (1 + S(t)).
# При t = медиане (S=1/2) -> ровно 1/3 (классика); t->0 -> 1/2; t=2 медианы (эксп.) -> 1/5.
import random, math
random.seed(5)
T = 2*10**6
def sample(dist):
    if dist == 'exp': return random.expovariate(math.log(2))      # медиана 1
    if dist == 'unif': return random.uniform(0, 2)                 # медиана 1
def S(dist, t):
    if dist == 'exp': return 2**(-t)
    if dist == 'unif': return max(0.0, 1 - t/2)
for dist in ('exp', 'unif'):
    bins = {}
    for _ in range(T):
        e = random.randint(1, 3)
        times = {c: sample(dist) for c in (2, 3) if c != e}         # только незаглушённые бомбы
        first = min(times, key=times.get)
        if first != 3: continue
        t = times[3]; b = min(int(t / 0.25), 11)
        st, n = bins.get(b, (0, 0)); bins[b] = (st + (e == 1), n + 1)
    print("dist=%s (median=1)" % dist)
    tot_st = tot_n = 0
    for b in sorted(bins):
        st, n = bins[b]; tot_st += st; tot_n += n
        tm = (b + 0.5) * 0.25; s = S(dist, tm)
        if n > 2000: print("  t~%.3f  P(stay) exact~%.4f MC %.4f (n=%d)" % (tm, s/(1+s), st/n, n))
    print("  averaged over t: P(stay) exact 0.3333 MC %.4f" % (tot_st/tot_n))
# точечная проверка у медианы: окно [0.95,1.05]
for dist in ('exp',):
    st = n = 0
    for _ in range(4*10**6):
        e = random.randint(1, 3)
        times = {c: sample(dist) for c in (2, 3) if c != e}
        first = min(times, key=times.get)
        if first == 3 and 0.95 < times[3] < 1.05: n += 1; st += e == 1
    print("window t in (0.95,1.05): P(stay) exact~0.3333 MC %.4f (n=%d)" % (st/n, n))
