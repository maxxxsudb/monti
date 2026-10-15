# R0-A: Астрон П1 "Очная ставка" (94.1%) и "Комитет Б" (модель с долей VIP v)
import random
random.seed(1)
N = 10**6
acc = 0.8

# --- 1. пара экспертов, отчёт только при согласии; оба сказали "честный"
exact = 0.5*acc*acc / (0.5*acc*acc + 0.5*(1-acc)**2)
hit = tot = 0
for _ in range(N):
    honest = random.random() < 0.5
    a = (random.random() < acc) == honest   # True = сказал "честный"
    b = (random.random() < acc) == honest
    if a and b:
        tot += 1; hit += honest
print("Очная ставка: P(честный | оба 'честный', согласны) exact=%.4f MC=%.4f" % (exact, hit/tot))
exact1 = 0.8
print("  один свидетель: 0.8 -> согласие пары СИЛЬНЕЕ (0.941>0.8), заголовок неверен")

# --- 2. Комитет Б: доля VIP v (90% пустышек, подписывают без проверки);
# обычные: 50% хороших, оба эксперта (точность 0.8) голосуют, видим 2 подписи если оба "за".
def exact_B(v):
    num = (1-v)*0.5*acc*acc + v*0.1
    den = (1-v)*(0.5*acc*acc + 0.5*(1-acc)**2) + v
    return num/den
# порог v*, где падает ниже 0.5
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo+hi)/2
    if exact_B(mid) > 0.5: lo = mid
    else: hi = mid
print("Комитет Б: порог доли VIP v*=%.4f (exact 0.15/0.55=%.4f)" % (lo, 0.15/0.55))
for v in (0.1, 0.3, 0.5):
    hit = tot = 0
    for _ in range(N//2):
        if random.random() < v:
            good = random.random() < 0.1; sig2 = True
        else:
            good = random.random() < 0.5
            a = (random.random() < acc) == good
            b = (random.random() < acc) == good
            sig2 = a and b
        if sig2:
            tot += 1; hit += good
    print("  v=%.1f P(хороший|2 подписи) exact=%.4f MC=%.4f" % (v, exact_B(v), hit/tot))
