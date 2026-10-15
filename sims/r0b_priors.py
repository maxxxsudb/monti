# §5 астра2: априоры 50/30/20, ведущий сохраняет защищённый i и одного чужого финалиста, не устраняя цель.
import random, itertools
pi=[0.5,0.3,0.2]
def exact(pi,i,q):  # q[i][j]: при цели в i ведущий оставляет j. Оптимальное решение после сообщения
    return sum(max(pi[i]*q[i][j],pi[j]) for j in range(3) if j!=i)
def uni(i): return {i:{j:0.5 for j in range(3) if j!=i}}
for i in range(3):
    q=uni(i)
    print("protect",i,"stay=%.4f switch=%.4f optimal=%.4f"%(pi[i],1-pi[i],exact(pi,i,q)))
print("random protect+switch exact=%.4f"%(sum(1-p for p in pi)/3))
# MC
rnd=random.Random(2); T=1_000_000
def play(i,policy):
    t=rnd.choices(range(3),pi)[0]
    others=[j for j in range(3) if j!=i]
    left= t if t!=i else rnd.choice(others)
    return (policy(i,left)==t)
fav_stay=sum(play(0,lambda i,l:i) for _ in range(T))/T
fav_opt =sum(play(0,lambda i,l: l if pi[l]>pi[i]*0.5 else i) for _ in range(T))/T
rnd_sw  =sum(play(rnd.randrange(3),lambda i,l:l) for _ in range(T))/T
dog_sw  =sum(play(2,lambda i,l:l) for _ in range(T))/T
print("MC: fav_stay=%.4f fav_opt=%.4f rand_switch=%.4f underdog_switch=%.4f"%(fav_stay,fav_opt,rnd_sw,dog_sw))
# попытка пробить V_i <= 1-pi_min случайными априорами и несимметричными ведущими
worst=0
for _ in range(200000):
    a=[rnd.random() for _ in range(3)]; s=sum(a); p=[x/s for x in a]
    for i in range(3):
        o=[j for j in range(3) if j!=i]; r=rnd.random()
        q={i:{o[0]:r,o[1]:1-r}}
        v=exact(p,i,q); worst=max(worst,v-(1-min(p)))
print("max over random cases of V_i-(1-pi_min) =",worst)
