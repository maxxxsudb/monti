# §7 астра2: избегающий/слепой/ищущий проверяющий (знает с вер. q), свободное предложение
import random
rnd=random.Random(4); T=1_000_000; q=0.5
def sim(kind):
    sw=n=0
    for _ in range(T):
        t=rnd.randrange(3); knows=rnd.random()<q
        if knows and kind=='avoid': c=[x for x in (1,2) if x!=t]; o=rnd.choice(c)
        elif knows and kind=='seek': o= t if t in (1,2) else rnd.choice((1,2))
        else: o=rnd.choice((1,2))
        if o==t: continue          # наблюдаем только «проверенный проигрышный»
        n+=1; sw+= (t==3-o)
    return sw/n
ex={'avoid':(1+q)/(2+q),'blind':0.5,'seek':(1-q)/(2-q)}
for k in ('avoid','blind','seek'): print(k,"MC=%.4f exact=%.4f"%(sim(k),ex[k]))
# свободное предложение: pi=1/3, alpha=0.9 (предлагает при верном), beta=0.3
pi,a,b=1/3,0.9,0.3; sw=n=0
for _ in range(T):
    right=rnd.random()<pi
    if rnd.random()<(a if right else b): n+=1; sw+=(not right)
print("offer MC=%.4f exact=%.4f"%(sw/n,(1-pi)*b/(pi*a+(1-pi)*b)))
