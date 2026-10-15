# §8 астра2: минное поле. Экспоненциальные часы, условие = «после N-2 взрывов выбранная клетка 0 цела».
import random, math
rnd=random.Random(5)
def R_exact(N,b): return (N-1)*math.gamma(N-1)*math.gamma(2-b)/math.gamma(N-b)
def sim_R(N,b,T):
    sw=n=0
    for _ in range(T):
        s=rnd.randrange(N)
        times=[math.inf if i==s else rnd.expovariate(1-b if i==0 else 1) if not (i==0 and b==1) else math.inf for i in range(N)]
        order=sorted(range(N),key=lambda i:times[i])
        if 0 in order[:N-2]: continue
        n+=1; sw+=(s!=0)
    return sw/n
for N,b in ((3,0.5),(5,0.5),(3,0.0),(4,1.0)):
    R=R_exact(N,b); print("N=%d beta=%.1f MC P_switch=%.4f exact R/(1+R)=%.4f"%(N,b,sim_R(N,b,400000),R/(1+R)))
# неизвестная защита: с вер. q клетка 0 полностью защищена (никогда не взрывается), иначе всё равноправно
def sim_unk(N,q,T):
    sw=n=0
    for _ in range(T):
        prot=rnd.random()<q; s=rnd.randrange(N)
        # порядок взрывов мин равномерно случаен; защищённая клетка — в конец
        mines=[i for i in range(N) if i!=s]; rnd.shuffle(mines)
        if prot and 0 in mines: mines.remove(0); mines.append(0)
        if 0 in mines[:N-2]: continue
        n+=1; sw+=(s!=0)
    return sw/n,n/T
for N,q in ((3,0.5),(100,0.1),(100,0.01)):
    mc,acc=sim_unk(N,q,1_000_000 if N==3 else 300000)
    print("unknown protection N=%d q=%.2f MC=%.4f exact=%.4f (accepted %.3f)"%(N,q,mc,(1+q*(N-2))/(2+q*(N-2)),acc))
# ожидание после первого взрыва, N=3, полная защита клетки 0
t0=1.0; win=0; n=0; sw_cond=sw_n=0
for _ in range(1_000_000):
    s=rnd.randrange(3)
    tm={i:(math.inf if (i==s or i==0) else rnd.expovariate(1)) for i in range(3)}
    ex=sorted([x for x in tm.values() if x<math.inf])
    if not ex: continue   # не бывает: хотя бы одна мина взрывается (s и 0 могут совпасть -> 2 мины)
    n+=1; t1=ex[0]
    second = len(ex)>1 and ex[1]<=t1+t0
    if second: win+=(s==0)
    else:
        rem=[i for i in (1,2) if tm[i]>t1][0]; win+=(s==rem); sw_n+=1; sw_cond+=(s==rem)
print("wait t=1: MC success=%.4f exact=%.4f | P_switch|no 2nd MC=%.4f exact=%.4f"%(win/n,1-math.exp(-t0)/3,sw_cond/sw_n,2/(2+math.exp(-t0))))
# информативность времени первого взрыва (выброшено в тексте): при s=0 горят 2 мины (инт. 2), иначе 1 мина (инт. 1)
# P(switch | t1) = (2/3)e^{-t1} / ((2/3)e^{-t1} + (1/3)*2e^{-2t1}) = 1/(1+e^{-t1})
print("с учётом времени первого взрыва: P_switch|t1 = 1/(1+e^-t1): t1=0 ->0.5, t1=2 ->%.3f"%(1/(1+math.exp(-2))))
