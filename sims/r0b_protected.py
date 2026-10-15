# §4 астра2: N=100, k=20 защищены, из 80 чужих ведущий оставляет m=5, не устраняя цель.
import random
from fractions import Fraction as F
N,k,m=100,20,5; T=1_000_000
print("exact: p_foreign_surv=",F(N-k,N*m)," p_protected=",F(1,N)," C=",F(N-k,m)," pair=",F(16,17))
rnd=random.Random(1)
fs=pr=0; pair_hit=pair_tot=0
for _ in range(T):
    t=rnd.randrange(N)
    foreign=list(range(k,N))
    if t>=k:
        others=[x for x in foreign if x!=t]
        surv=[t]+rnd.sample(others,m-1)
    else:
        surv=rnd.sample(foreign,m)
    s=rnd.choice(surv)           # конкретный чужой выживший
    fs+= (t==s); pr+=(t==0)      # конкретный защищённый #0
    if t==s or t==0:
        pair_tot+=1; pair_hit+=(t==s)
print("MC: foreign_surv=%.4f protected=%.4f pair=%.4f (16/17=%.4f)"%(fs/T,pr/T,pair_hit/pair_tot,16/17))
# несимметричный ведущий: при цели в чужой группе всегда сохраняет её + (m-1) с наименьшими номерами;
# при цели в защищённой — m с наименьшими номерами. Проверка критерия A/k=B/(N-k):
cnt={}; T2=1_000_000
for _ in range(T2):
    t=rnd.randrange(N)
    if t>=k:
        rest=[x for x in range(k,N) if x!=t][:m-1]; surv=tuple(sorted([t]+rest))
    else: surv=tuple(range(k,k+m))
    if surv==tuple(range(k,k+m)): cnt[t<k]=cnt.get(t<k,0)+1
tot=sum(cnt.values())
print("asym host, e = 'остались 20..24': P(target in protected)=%.4f (prior %.2f); exact=%s"%(cnt.get(True,0)/tot,k/N,F(k,k+m)))
