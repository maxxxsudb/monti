# r0c_static: C=(N-k)/m invariant, R=C under exchangeable target-preserving filter; biased filter breaks it (Monty Crawl)
import random
from math import comb
random.seed(7); T = 10**6
N, k, m = 10, 3, 2
Y = list(range(k)); O = list(range(k, N)); n = N - k
def filt(tau):
    if tau in O:
        rest = [j for j in O if j != tau]; return frozenset([tau] + random.sample(rest, m-1))
    return frozenset(random.sample(O, m))
s0 = frozenset([3, 4]); hits = 0; cnt = {}
for _ in range(T):
    tau = random.randrange(N); s = filt(tau)
    if s == s0: hits += 1; cnt[tau] = cnt.get(tau, 0) + 1
print(f"N={N},k={k},m={m}, observed s={{3,4}}, {hits} hits")
print(f"P(tau in Y|s)={sum(cnt.get(i,0) for i in Y)/hits:.4f} exact k/N={k/N:.4f}")
for j in (3, 4): print(f"P(tau={j}|s)={cnt.get(j,0)/hits:.4f} exact (N-k)/(Nm)={(n)/(N*m):.4f}")
print(f"P(tau=0|s)={cnt.get(0,0)/hits:.4f} exact 1/N={1/N:.4f}")
print(f"R = C(n,m)/C(n-1,m-1) = {comb(n,m)/comb(n-1,m-1):.4f} = C=(N-k)/m={n/m:.4f}; MC R={cnt.get(3,0)/cnt.get(0,1):.4f}")
# biased classic Monty (N=3): host with goat choice opens door 2 w.p. q (Monty Crawl). Observed: door 1 opened.
for q in (0.5, 1.0):
    st = sw = c = 0
    for _ in range(T):
        car = random.randrange(3)
        opened = (2 if random.random() < q else 1) if car == 0 else (2 if car == 1 else 1)
        if opened != 1: continue
        c += 1; st += car == 0; sw += car == 2
    print(f"biased host q={q}, door1 opened: stay={st/c:.4f} sw={sw/c:.4f} exact stay=(1-q)/(2-q)={(1-q)/(2-q):.4f}")
