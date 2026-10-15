# r0d_qbeta.py -- частичная осведомлённость q и щит beta из 'монтихол от сонет' (табл. 1.7)
import random
from math import gamma
random.seed(2)
T = 10**6

# q-модель: k=1,m=1; с вер. q ведущий знает (оставляет цель), иначе открывает N-2 случайных из O;
# наблюдение: среди открытых нет приза. Игрок НЕ знает, какой был режим.
def q_sim(N, q):
    st = sw = 0
    for _ in range(T):
        tau = random.randint(1, N); O = list(range(2, N+1))
        if random.random() < q:
            surv = tau if tau != 1 else random.choice(O)
        else:
            surv = random.choice(O)
            if tau != 1 and tau != surv: continue  # приз открыт -> отбраковка
        st += tau == 1; sw += tau == surv
    return st, sw
for N, q in [(3, 0.5), (5, 0.5), (10, 0.3)]:
    st, sw = q_sim(N, q); R = q*(N-2)+1
    print("q: N=%d q=%.1f  R exact %.4f MC %.4f | P(switch) exact %.4f MC %.4f" % (N, q, R, sw/st, R/(1+R), sw/(st+sw)))

# beta-модель (реконструкция): N ячеек, N-1 бомб, 1 пустая (цель). Каждая бомба взрывается в Exp(1),
# ваша (ячейка 1) -- в Exp(1-beta). Наблюдаем момент, когда осталось ровно 2 невзорванные: ваша и j.
def S_N(N, b): return gamma(N-1)*gamma(2-b)/gamma(N-b)
def beta_sim(N, b):
    st = sw = 0
    for _ in range(T):
        tau = random.randint(1, N)
        t = {}
        for c in range(1, N+1):
            if c == tau: t[c] = float('inf')
            elif c == 1: t[c] = random.expovariate(1-b) if b < 1 else float('inf')
            else: t[c] = random.expovariate(1.0)
        order = sorted(t, key=t.get)  # первые N-2 взорвались
        rem = order[N-2:]
        if 1 not in rem: continue      # ваша взорвалась раньше -> другая ветка
        j = rem[0] if rem[1] == 1 else rem[1]
        st += tau == 1; sw += tau == j
    return st, sw
for N, b in [(3, 0.5), (4, 0.5), (6, 0.8)]:
    st, sw = beta_sim(N, b); R = (N-1)*S_N(N, b)
    print("beta: N=%d b=%.1f R exact %.4f MC %.4f | P(switch|you&j remain) exact %.4f MC %.4f" % (N, b, R, sw/st, R/(1+R), sw/(st+sw)))
