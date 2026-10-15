# R0-A: астра п.2/10В "информативное молчание" (10% -> 100%) и Астрон П6 "Синхронное молчание"
import random
random.seed(6)
N = 10**6

# --- астра: исправное 1 мин(0.9)/60(0.1); неисправное 1(0.1)/10(0.9); prior 0.5
def T(ok):
    if ok: return 1 if random.random() < 0.9 else 60
    return 1 if random.random() < 0.1 else 10
for t, ex in ((2, 0.1), (11, 1.0)):
    c = h = 0
    for _ in range(N):
        ok = random.random() < 0.5
        if T(ok) > t: c += 1; h += ok
    print("астра: P(исправно|молчит >%d мин) exact=%.3f MC=%.4f" % (t, ex, h/c))

# --- Астрон П6: H1 (ошибка): 1ч(0.8)/10ч(0.2); H0 (чисто): 3ч(0.9)/10ч(0.1); prior 0.5
def law(err):
    if err: return 1 if random.random() < 0.8 else 10
    return 3 if random.random() < 0.9 else 10
def exact(n, t, common):
    S0 = (1.0 if t < 3 else 0.1) if t < 10 else 0.0
    S1 = (0.2 if t >= 1 else 1.0) if t < 10 else 0.0
    L0 = S0**n
    L1 = S1 if common else S1**n
    return L0/(L0+L1)
for common in (False, True):
    for n in (1, 2):
        for t in (2, 4):
            c = h = 0
            for _ in range(N//2):
                err = random.random() < 0.5
                if err and common:
                    ts = [law(True)]*n           # общая причина: оба застревают вместе
                else:
                    ts = [law(err) for _ in range(n)]
                if min(ts) > t: c += 1; h += (not err)
            print("П6 %s n=%d t=%dч: P(чисто|все молчат) exact=%.4f MC=%.4f"
                  % ("общая" if common else "незав.", n, t, exact(n, t, common), h/c))
