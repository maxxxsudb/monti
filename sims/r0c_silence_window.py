# r0c_silence_window: (1) silence odds reversal via hazard crossing; (2) common-cause reliability; (3) window max of S*kappa
import random, math
random.seed(5); T = 10**6
# (1) candidate: prior good 1/2. Good: offer at U(0,2) days w.p. .6, else (slow committee) U(7,14). Bad: auto-reject at U(3,7).
def resp(good):
    if good: return random.uniform(0,2) if random.random() < .6 else random.uniform(7,14)
    return random.uniform(3,7)
def S(good, t):
    if good:
        a = .6*max(0, 1-t/2) ; b = .4*(1 if t<7 else max(0,(14-t)/7)); return a+b
    return 1 if t < 3 else max(0, (7-t)/4)
samples = [(g, resp(g)) for g in (random.random() < .5 for _ in range(T))]
for t in (0, 1, 2.5, 4, 5, 6, 6.9):
    alive = [g for g, r in samples if r > t]
    pg = sum(alive)/len(alive)
    ex = S(True,t)/(S(True,t)+S(False,t))
    print(f"t={t:4}: P(good | silence till t) MC={pg:.4f} exact={ex:.4f}")
# (2) common-cause: P(both fail)=q^2+rho q(1-q)
for q, rho in ((0.1, 0.0), (0.05, 0.2)):
    both = q*q + rho*q*(1-q); n = 0
    for _ in range(T):
        u = random.random()
        n += u < both
    # direct construction: with prob rho shared fail-draw, else independent (gives corr rho)
    m = 0
    for _ in range(T):
        if random.random() < rho:
            f = random.random() < q; m += f
        else:
            m += (random.random() < q) and (random.random() < q)
    print(f"q={q} rho={rho}: exact P(both fail)={both:.5f}  MC(shared-shock model)={m/T:.5f}")
# (3) window: S(t)=exp(-t), kappa(t)=t -> F=t e^-t, max at t=1 where dlnk/dt=1/t = h=1; second order F''<0
F = lambda t: t*math.exp(-t)
ts = [i/1000 for i in range(1, 5001)]; tm = max(ts, key=F)
print(f"window: argmax F = {tm:.3f} (exact 1), F''(1)={(F(1.001)-2*F(1)+F(0.999))/1e-6:.4f} <0")
# MC toy: each unit has fixation time tau~Exp(1); action at time t flips outcome w.p. kappa(t)=min(1,t/3) if tau>t
best = None
for t in (0.25, 0.5, 1, 1.5, 2, 3):
    n = T; w = 0
    for _ in range(n):
        if random.expovariate(1) > t and random.random() < min(1, t/3): w += 1
    ex = math.exp(-t)*min(1, t/3); print(f"  act at t={t}: success MC={w/n:.4f} exact={ex:.4f}")
print("  exact argmax of e^-t * t/3 on [0,3] is t=1 (=0.1226)")
