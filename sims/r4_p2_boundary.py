from itertools import permutations
from fractions import Fraction as F
import random

states=list(permutations(('E','D','N')))
same=swap=veto=correct_veto=novice=0
rng=random.Random(20261018)
for _ in range(1_000_000):
    s=rng.choice(states)
    r1=rng.choice([j for j in (1,2) if s[j]!='E'])
    r2=rng.choice([j for j in (0,2) if s[j]!='D'])
    if r1==2 and r2==2:
        same+=1
        swap+=s[1]=='E' and s[0]=='D'
    choices=[j for j in (0,2) if j!=r1 and s[j]!='D']
    if r1==2 and not choices:
        veto+=1
        correct_veto+=s[1]=='E' and s[0]=='D'
    # Distinct specialities: each filter preserves its own specialist.
    cut1=rng.choice([j for j in range(3) if s[j]!='E'])
    rem=[j for j in range(3) if j!=cut1]
    cut2=rng.choice([j for j in rem if s[j]!='D'])
    final=next(j for j in rem if j!=cut2)
    novice+=s[final]=='N'
print('reciprocal independent rejection:', 'exact',F(4,5),'MC',swap/same,'condition count',same)
print('adaptive veto:', 'exact',1,'MC',correct_veto/veto,'condition count',veto)
print('different-speciality cascade:', 'exact',F(1,4),'MC',novice/1_000_000)
