# R0-A: астра §3 (N=100,k=20,m=5 -> 16%), §4/10А (защита худшей двери 50/30/20),
# 10Б (прогрессивный Монти, 4 двери), §5 (обмен предлагается с вер. alpha/beta),
# Астрон 3.1 (временной Монти: delta = lam*(N-k-m)/(N m))
import random
random.seed(8)
N = 10**6

# --- §3: N=100, k=20, m=5, информированный симметричный отсев
c = 0; M = 200000
for _ in range(M):
    tau = random.randrange(100)       # защищены 0..19
    O = list(range(20, 100))
    if tau >= 20:
        others = [x for x in O if x != tau]
        surv = [tau] + random.sample(others, 4)
    else:
        surv = random.sample(O, 5)
    j = random.choice(surv)           # конкретный чужой выживший
    c += (j == tau)
print("§3 p_чужого exact=0.16 MC=%.4f" % (c/M))

# --- 10А: приоры 0.5/0.3/0.2
pri = [0.5, 0.3, 0.2]
def play(prot, strat, tie="uniform"):
    w = 0
    for _ in range(N//4):
        r = random.random()
        prize = 0 if r < 0.5 else (1 if r < 0.8 else 2)
        others = [d for d in range(3) if d != prot]
        if prize == prot:
            keep = random.choice(others) if tie == "uniform" else others[-1]
        else:
            keep = prize
        final = strat(prot, keep)
        w += (final == prize)
    return w/(N//4)
stay = lambda p, k: p
switch = lambda p, k: k
# оптимальная адаптивная при защите 0 и равномерном тай-брейке: перейти, если keep=1
adapt = lambda p, k: k if pri[k] > pri[p]*0.5 else p
adapt_det = lambda p, k: k if k == 1 else p   # детерминированный ведущий оставляет дверь 2 (индекс 2)
print("10А: остаться на 50%%: %.4f (0.5)" % play(0, stay))
print("10А: защитить 50%%, адаптивно (равн.): %.4f (0.55)" % play(0, adapt))
print("10А: случайная защита + switch: %.4f (0.6667)" % (sum(play(p, switch) for p in range(3))/3))
print("10А: защитить 20%% + switch: %.4f (0.8)" % play(2, switch))
print("10А: защитить 50%%, ведущий детерм. оставляет 3-ю, адаптивно: %.4f (0.8)" % play(0, adapt_det, tie="det"))

# --- 10Б: 4 двери, последовательное исключение
def prog(follow_leader):
    w = 0
    for _ in range(N//2):
        prize = random.randrange(4)
        prot = 0
        alive = [0, 1, 2, 3]
        # первое исключение
        cand = [d for d in alive if d != prot and d != prize]
        alive.remove(random.choice(cand))
        if follow_leader:
            prot = random.choice([d for d in alive if d != 0])   # лидер 3/8
        cand = [d for d in alive if d != prot and d != prize]
        alive.remove(random.choice(cand))
        final = [d for d in alive if d != prot][0]
        w += (final == prize)
    return w/(N//2)
print("10Б: держать исходную, switch в конце: %.4f (0.75)" % prog(False))
print("10Б: перейти к лидеру, switch в конце: %.4f (0.625)" % prog(True))

# --- §5: обмен предлагается с вер. alpha (выбор верен) / beta (неверен), 3 двери
for a, b in ((1, 1), (1, 0.5), (0.5, 0.2)):
    off = win = 0
    for _ in range(N//4):
        right = random.random() < 1/3
        if random.random() < (a if right else b):
            off += 1; win += (not right)
    ex = (2/3)*b/((1/3)*a + (2/3)*b)
    print("§5 alpha=%.1f beta=%.1f: P(обмен выигрывает|предложение) exact=%.4f MC=%.4f" % (a, b, ex, win/off))

# --- Астрон 3.1: N=7,k=2,m=2, lam=0.6
Nn, k, m, lam = 7, 2, 2, 0.6
st = sw = 0
for _ in range(N//2):
    Y = [0, 1]; O = list(range(2, Nn))
    if random.random() < lam:
        tau = random.randrange(Nn)
        if tau in O:
            surv = [tau] + random.sample([x for x in O if x != tau], m-1)
        else:
            surv = random.sample(O, m)
    else:
        surv = random.sample(O, m)
        tau = random.choice(Y + surv)
    st += (tau == 0)
    sw += (tau == random.choice(surv))
ex = lam*(Nn-k-m)/(Nn*m)
print("3.1: P_switch-P_stay exact=%.4f MC=%.4f (P_stay=%.4f, P_switch=%.4f)" % (ex, (sw-st)/(N//2), st/(N//2), sw/(N//2)))
