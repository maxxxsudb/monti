# астра2 §9,§10,§11,§13,§14,§15 + бытовые #24 (автобус)
import random, math
rnd=random.Random(6); T=1_000_000
# §9: N=3, phi=1, d=1/3: граница w
for r in (0,0.1):
    d,phi=1/3,1; print("§9 r=%.1f w*=%.4f"%(r,(r+2*phi-1)/(d+2*phi-1)))
# §10 батарейки
c=[0,0,0];cA1=[0,0];cA0=[0,0];rep=[0,0]
for _ in range(T):
    a,b=rnd.random()<.5,rnd.random()<.5
    if not(a or b): continue
    c[0]+=1;c[1]+=b
    if a: cA1[0]+=1;cA1[1]+=b
    else: cA0[0]+=1;cA0[1]+=b
print("§10 P(B)=%.4f P(B|A=1)=%.4f P(B|A=0)=%.4f (2/3,1/2,1); замена A после покупки P(B)=%.4f"%(c[1]/c[0],cA1[1]/cA1[0],cA0[1]/cA0[0],c[1]/c[0]))
# §11 тест точности w
w=0.7;s=0
for _ in range(T):
    A=rnd.random()<.5; sig=A if rnd.random()<w else not A
    s+= rnd.random()<0.9 if sig==A else rnd.random()<0.1
print("§11 w=0.7 MC=%.4f exact=%.4f"%(s/T,0.1+0.8*w))
# §13 резервирование: коррелированные отказы
f0,f1=0.1,0.05; rho_star=(f0**2-f1**2)/(f1*(1-f1)); print("§13 rho*=%.4f"%rho_star)
rho=0.2; p11=f1*f1+rho*f1*(1-f1); both=0
for _ in range(T):
    u=rnd.random()
    both+= u<p11
print("§13 rho=0.2: P(both fail) MC=%.5f vs independent f0^2=%.5f -> хуже: %s"%(both/T,f0**2,both/T>f0**2))
# §14 Браесс: численное равновесие (поток по 3 путям, проекция/наилучший ответ малыми шагами)
def eq(l,Q=4000.0):
    x=[Q/3]*3  # SAT, SBT, SABT
    for it in range(200000):
        sa=x[0]+x[2]; bt=x[1]+x[2]
        c=[sa/100+45, 45+bt/100, sa/100+l+bt/100]
        j=min(range(3),key=lambda i:c[i]); k=max(range(3),key=lambda i:c[i] if x[i]>1e-9 else -1)
        if c[k]-c[j]<1e-7: break
        mv=min(x[k],(c[k]-c[j])*20); x[k]-=mv; x[j]+=mv
    sa=x[0]+x[2]; bt=x[1]+x[2]
    c=[sa/100+45, 45+bt/100, sa/100+l+bt/100]
    return max(c[i] for i in range(3) if x[i]>1e-6)
def formula(l): return 80+l if l<=5 else (90-l if l<=25 else 65)
print("§14 l: numeric / formula:",[(l,round(eq(l),3),formula(l)) for l in (0,2,5,10,20,25,30)])
# §15 порог: r=1, theta=1/2
th=0.5; f=lambda x:x*(1-x)*(x-th)
xm=(1+th-math.sqrt(1-th+th*th))/3; uc=-f(xm); print("§15 x_m=%.6f u_c=%.7f"%(xm,uc))
def simpson(g,a,b,n):
    h=(b-a)/n; s=g(a)+g(b)
    for i in range(1,n): s+=(4 if i%2 else 2)*g(a+i*h)
    return s*h/3
def Tu(u):
    g=lambda x:1/(u+f(x))
    # дробим отрезок у x_m для почти-сингулярности
    return sum(simpson(g,a,b,20000) for a,b in ((0,xm-0.02),(xm-0.02,xm+0.02),(xm+0.02,th)))
for m in (1.02,2,20):
    t=Tu(m*uc); print("§15 u=%.2fu_c T=%.3f D=%.4f"%(m,t,m*uc*t))
# u* для J2=u^2 T(u): золотое сечение
lo,hi=1.05,4.0
for _ in range(60):
    a=lo+(hi-lo)*0.382; b=lo+(hi-lo)*0.618
    if (a*uc)**2*Tu(a*uc) < (b*uc)**2*Tu(b*uc): hi=b
    else: lo=a
print("§15 u*/u_c=%.4f"%((lo+hi)/2))
# #24 автобус: интервалы 5 и 15 чередуются
per=20; w=0
for _ in range(T):
    t=rnd.random()*per; w+= (5-t) if t<5 else (20-t)
print("#24 bus MC=%.4f exact=6.25"%(w/T))
