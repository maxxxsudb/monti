import math
import random

rng=random.Random(20261019)
n=1_000_000
t=math.log(2)
for alpha,gamma in [(0,1),(1,2),(1,1)]:
    for r in [1,0]:
        alive=safe_alive=0
        for _ in range(n):
            safe=rng.random()<.5
            hazard=r*(alpha if safe else gamma)
            survived=rng.random()<math.exp(-hazard*t)
            alive+=survived
            safe_alive+=survived and safe
        exact=math.exp(-r*alpha*t)/(math.exp(-r*alpha*t)+math.exp(-r*gamma*t))
        print('rates',alpha,gamma,'shield factor',r,'exact',exact,'MC',safe_alive/alive)
foreign_safe=0
for _ in range(n):
    safe=rng.randrange(3)
    foreign_safe+=safe!=0
print('one intrinsically safe, full shield, stop after first foreign blast; exact 2/3 MC',foreign_safe/n)
