# R0-A: астра §9 бистабильная модель (детерминированная проверка), r=1, theta=1/2
import math
r, th = 1.0, 0.5
f = lambda x: r*x*(1-x)*(x-th)
xm = (1+th-math.sqrt(1-th+th*th))/3
uc = r*xm*(1-xm)*(th-xm)
print("x_m=%.6f u_c=%.7f (заявлено 0.0481125)" % (xm, uc))

def T(u, n=2_000_000):
    h = th/n
    return sum(h/(u+f((i+0.5)*h)) for i in range(n))

for mult, claimT, claimD in ((1.02, 100.39, 4.927), (2, 8.07, 0.776), (20, 0.537, 0.517)):
    u = mult*uc; t = T(u)
    print("u=%gu_c: T=%.3f (%.3f) D=%.3f (%.3f)" % (mult, t, claimT, u*t, claimD))

# минимум J(u)=u^2 T(u), золотое сечение по mult
J = lambda mlt: (mlt*uc)**2*T(mlt*uc, 200_000)
a, b = 1.05, 4.0
gr = (math.sqrt(5)-1)/2
c, d = b-gr*(b-a), a+gr*(b-a)
for _ in range(40):
    if J(c) < J(d): b = d
    else: a = c
    c, d = b-gr*(b-a), a+gr*(b-a)
print("u*/u_c=%.4f (заявлено 1.6103)" % ((a+b)/2))
