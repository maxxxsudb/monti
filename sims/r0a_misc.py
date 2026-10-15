# R0-A: астра п.1/10Г (компенсация), п.3 (батарейки), п.4/10Д (блоки питания), п.5 (Браесс),
# §2 (порог 60%), §6 (s>0.7368), §7 (t*=1/h, 1/(h+g)), Астрон П3 (инверсия рекорда: арифметика)
import random, math
random.seed(9)
N = 10**6

# п.1 компенсация: детерминированно (Фреше-границы), MC для примера
def bounds(p0, p1): return abs(p1-p0), min(p0+p1, 2-p0-p1)
print("п.1 границы M при p0=p1=0.5:", bounds(0.5, 0.5))
s_off = s_on = s_tgt = 0
for _ in range(N):
    typeA = random.random() < 0.5
    s_off += typeA; s_on += (not typeA); s_tgt += 1
print("п.1 MC: выкл=%.4f вкл=%.4f по типу=%.4f" % (s_off/N, s_on/N, s_tgt/N))

# п.3 батарейки
cS = bS = cA = bA = c0 = b0 = 0
for _ in range(N):
    a = random.random() < 0.5; b = random.random() < 0.5
    if not (a or b): continue
    cS += 1; bS += b
    if a: cA += 1; bA += b
    else: c0 += 1; b0 += b
print("п.3 P(B|S)=%.4f (2/3) P(B|S,A=1)=%.4f (1/2) P(B|S,A=0)=%.4f (1)" % (bS/cS, bA/cA, b0/c0))

# п.4 блоки
old = new = 0
for _ in range(N):
    old += (random.random() < 0.9) or (random.random() < 0.9)
    new += not (random.random() < 0.05)
print("п.4 R_old=%.4f (0.99) R_new=%.4f (0.95) rho*=%.4f" % (old/N, new/N, (0.01-0.0025)/(0.05*0.95)))

# п.5 Браесс (детерминированно)
T_old = 2000/100 + 45; T_new = 40 + 0 + 40; T_dev = 40 + 45
print("п.5 Браесс: old=%g new=%g deviate=%g" % (T_old, T_new, T_dev))

# §2 порог
print("§2 p > (1+0.2)/2 =", (1+0.2)/2)
# §6
print("§6 s* = 0.70/0.95 = %.4f" % (0.70/0.95))
# §7: G=a t e^{-ht}; G/C = a t e^{-(h+g)t}; численно h=0.3,g=0.2
h, g = 0.3, 0.2
ts = [i/10000 for i in range(1, 200000)]
t1 = max(ts, key=lambda t: t*math.exp(-h*t)); t2 = max(ts, key=lambda t: t*math.exp(-(h+g)*t))
print("§7 t*=%.4f (1/h=%.4f), t*cost=%.4f (1/(h+g)=%.4f)" % (t1, 1/h, t2, 1/(h+g)))

# Астрон П3: арифметика при заявленных 0.9 / 0.5
print("П3: A: %.3f  B: %.3f" % (0.9*0.05+0.1*0.55, 0.5*0.05+0.5*0.55))
# Проверка "C=8 => 90% органических": 10 проектов, 5 органических; 1 по квоте (случайный),
# из 9 остальных "конкурс" (идеальный) выбирает органического, если он есть.
cnt = org = 0
for _ in range(N//4):
    types = [1]*5 + [0]*5; random.shuffle(types)
    quota = types[0]; rest = types[1:]
    winner = 1 if any(rest) else 0
    cnt += 1; org += winner
print("П3 модель идеального конкурса: P(победитель органич.)=%.4f (не 0.9; 0.9 из C не следует)" % (org/cnt))
