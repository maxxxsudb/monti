# §6 астра2: последовательный отсев, порог ожидания, «парадокс текущего лидера» (4 двери)
import random
from fractions import Fraction as F
rnd=random.Random(3); T=1_000_000
N=10
print("exact c_j:",[str(F(N-1,N*(N-1-j))) for j in range(N-1)])
print("exact last-step gain=",F(N-1,2*N)," earlier total=",F(N-3,2*N)," delta*=",F(N-3,2*(N-2)))
# MC: N=10, держим дверь 0, ведущий по одному убирает случайную проигрышную чужую
def run(delta, keep_zero_on_loss=False):
    w_now=w_wait=0
    for _ in range(T//5):
        t=rnd.randrange(N); alive=list(range(1,N))
        while len(alive)>2:
            c=[x for x in alive if x!=t]; alive.remove(rnd.choice(c))
        # сейчас: переход к случайной из двух чужих (окончательно)
        w_now+= (rnd.choice(alive)==t)
        # ждать: последний отсев
        c=[x for x in alive if x!=t]; alive.remove(rnd.choice(c))
        if rnd.random()<delta: w_wait+=(alive[0]==t)
        else: w_wait+= 0 if keep_zero_on_loss else (t==0)
    return w_now/(T//5), w_wait/(T//5)
for d in (0.40,0.4375,0.47):
    a,b=run(d); print("delta=%.4f MC now=%.4f wait=%.4f | exact now=%.4f wait=%.4f"%(d,a,b,(N-1)/(2*N),d*(N-1)/N+(1-d)/N))
# скрытое допущение: если «переключиться сейчас» не окончательно (после отсева можно переключиться снова, право сохраняется с delta)
# то немедленный переход к X и затем финальный переход: защищён X (вероятн. 9/20), после отсева переход -> 1-9/20=11/20 (с вер. delta), иначе остаться с X
d=0.4375
print("switch-now-not-final exact: delta*(1-9/20)+(1-delta)*9/20 =",d*11/20+(1-d)*9/20," vs wait",d*0.9+(1-d)*0.1)
# 4 двери: лидер
w_lead=w_keep=0
for _ in range(T):
    t=rnd.randrange(4); alive=[1,2,3]
    c=[x for x in alive if x!=t]; alive.remove(rnd.choice(c))
    # стратегия A: сохраняем 0, в конце переключаемся
    a2=alive[:]; c=[x for x in a2 if x!=t]; a2.remove(rnd.choice(c)); w_keep+=(a2[0]==t)
    # стратегия B: защищаем чужого лидера X=alive[0]; ведущий убирает проигрышную из {0, alive[1]}; переключаемся на оставшуюся
    X=alive[0]; pool=[0,alive[1]]; c=[x for x in pool if x!=t]; pool.remove(rnd.choice(c)); w_lead+=(pool[0]==t)
print("4 doors MC keep=%.4f (3/4) leader=%.4f (5/8)"%(w_keep/T,w_lead/T))
