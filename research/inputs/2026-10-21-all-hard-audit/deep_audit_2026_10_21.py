#!/usr/bin/env python3
"""Independent audit of selected claims in solutions_all_hard_tasks_2026_10_21.md."""
import itertools
import math
from fractions import Fraction
from scipy.stats import binom
import numpy as np


def f(a): return 2*a/(1+a)

def D(a,b,c):
    return np.array([[x-f(x), 0.5-f(x), 2/3-f(x)] for x in (a,b,c)])

def leb_weights(x,pts):
    out=[]
    for i,z in enumerate(pts):
        t=(1+z)/(1+x)
        for j,k in enumerate(pts):
            if i != j: t *= (x-k)/(z-k)
        out.append(t)
    return np.array(out)

print('N1 - matrix identity and certified node comparison')
for a,c in [(0.,1.),(.1,.9),(0.,.5)]:
    b=math.sqrt((1+a)*(1+c))-1
    inv=np.linalg.inv(D(a,b,c))
    norms=np.abs(inv).sum(axis=1)
    w2=(1+b)/((b-a)*(c-b));rp=2*w2
    pred=np.array([rp, 6+2*(2*a*c-a-c+1)*rp, 6+1.5*(3*a*c-a-c+1)*rp])
    errs=[]
    for x in np.linspace(a,c,1001):
        t=leb_weights(x,(a,b,c))
        errs.append(max(0, (t*t).sum()-1))
    print(f'  interval [{a:g},{c:g}]: b*={b:.9f}; rows={norms.round(6)}; formula_err={max(abs(norms-pred)):.2e}; max_sq_excess={max(errs):.2e}')
for pts in [(0.,.25,.5),(0.,.4,1.),(.1,.45,.9)]:
    norm=np.abs(np.linalg.inv(D(*pts))).sum(axis=1).max()
    print(f'  rational nodes {pts}: ||D^(-1)||_inf={norm:.9f}')

print('\nN2 - test the stated Hoeffding-level guarantee s_l at eta=.2')
eta=.2
for ell in [1,3,5,6]:
    n=math.ceil(16/(9*eta*eta)*math.log(32*ell*ell))
    p=.5+eta
    cutoff=.5+5*eta/8
    actual=binom.cdf(math.floor(n*cutoff),n,p)
    alleged=1/(16*ell*ell)
    print(f'  ell={ell}: n={n}, exact Bernoulli failure={actual:.9f}, claimed bound={alleged:.9f}, violated={actual>alleged}')
print('  N2 plateaus measure = 4*omega; for omega=0.30 this equals 1.20 > 1 (construction impossible).')

print('\nR1 - true minimum separation of all five structural profiles')
for gamma,epsilon in [(.7,.49),(.6,.3),(.9,.1)]:
    pr={'N':(1,1,1), 'L':(gamma,epsilon,gamma),
        'W':(epsilon,gamma,gamma), 'E':(epsilon,epsilon,epsilon),
        'L+W':(epsilon**2,epsilon**2,gamma**2)}
    ds=sorted((max(abs(x-y) for x,y in zip(p,q)),a,b) for (a,p),(b,q) in itertools.combinations(pr.items(),2))
    text_claim=min(gamma-epsilon,abs(gamma**2-epsilon))
    correct=min(gamma-epsilon,max(epsilon*(1-epsilon),abs(gamma**2-epsilon)))
    print(f'  gamma={gamma:g} epsilon={epsilon:g}: enumerated={ds[0][0]:.9f} ({ds[0][1]},{ds[0][2]}), claimed={text_claim:.9f}, corrected={correct:.9f}')
pr={'N':(1,1),'L':(.9,.1),'W':(.1,.9),'E':(.1,.1),'L+W':(.01,.01)}
print('  fixed gamma=.9 epsilon=.1, two-probe signatures:',pr,'; distinct=',len(set(pr.values()))==5)
print('  Structural independence demands L+W = (gamma*epsilon, gamma*epsilon, gamma**2), NOT (epsilon**2,epsilon**2,gamma**2)')
for gamma,epsilon in [(.7,.49),(.6,.3),(.9,.1)]:
    pr={'N':(1,1,1),'L':(gamma,epsilon,gamma), 'W':(epsilon,gamma,gamma), 'E':(epsilon,epsilon,epsilon), 'L+W':(gamma*epsilon,gamma*epsilon,gamma**2)}
    ds=sorted((max(abs(x-y) for x,y in zip(p,q)),a,b) for (a,p),(b,q) in itertools.combinations(pr.items(),2))
    calc=min(gamma-epsilon,max(epsilon*(1-gamma),abs(gamma**2-epsilon)))
    print(f'  REPAIRED gamma={gamma:g} epsilon={epsilon:g}: enumerated={ds[0][0]:.9f} ({ds[0][1]},{ds[0][2]}); formula={calc:.9f}')
print('\nR3 - false L_eff equivalence')
for sl in [.9,.99,.9999]:
    a=math.sqrt(1-sl**2); b=1-sl
    print(f'  L=1 slope={sl}: sqrt(L^2-s^2)={a:.7f}; L-|s|={b:.7f}; ratio={a/b:.3f}')

print('\nR4 - independent exact fractions for both paradoxes')
pC1_A=Fraction(1,2)
pC1_B=Fraction(1,1)/(Fraction(1,1)+Fraction(1,3))
pC2_F=Fraction(3,4)/(Fraction(3,4)+Fraction(2,4))
pC2_S=(Fraction(1,4)*Fraction(3,3))/(Fraction(1,4)*Fraction(3,3)+Fraction(2,4)*Fraction(2,3))
print('  C1:',pC1_A,pC1_B,'; C2:',pC2_F,pC2_S)
