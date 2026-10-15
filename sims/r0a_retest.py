# R0-A: Астрон П2 "Проклятие второго шанса" (75% vs 30%)
import random
random.seed(2)
N = 10**6
pR, pH = 0.9, 0.3
e1 = 0.5*pR/(0.5*pR+0.5*pH)
e2 = 0.5*(1-pR)*pR/(0.5*(1-pR)*pR+0.5*(1-pH)*pH)
c1 = r1 = c2 = r2 = 0
for _ in range(N):
    rel = random.random() < 0.5
    p = pR if rel else pH
    if random.random() < p:
        c1 += 1; r1 += rel
    elif random.random() < p:
        c2 += 1; r2 += rel
print("P(Надёжный|1 тест) exact=%.4f MC=%.4f" % (e1, r1/c1))
print("P(Надёжный|2 теста) exact=%.4f MC=%.4f" % (e2, r2/c2))
