#!/usr/bin/env python3
"""Independent exact checks of the new October 21 proposed claims.
Uses standard library and SymPy for ONE symbolic factorization.
Does not claim to empirically validate N2 minimax or R3 minimax conjectures.
"""
from fractions import Fraction as Q
from math import ceil, exp, log
from itertools import combinations
from sympy import symbols, expand, factor

n,a,b=symbols('n a b', integer=True)
D = n*(a*(a-1)*(n-a)+b*(b-1)*(n-b))-(n-2)*a*b*(2*n-a-b)
compact=(a+b-n)*((a+b)*(2*n-a-b)-(2*n-1)*(a-b)**2)/2
assert expand(D-compact)==0
print('CHEST: exact identity verified by symbolic expansion.')
print('       D = (a+b-n)/2 * [(a+b)(2n-a-b)-(2n-1)(a-b)^2]')

def outcomes(N,A,B):
    wA=A*(N-A)
    wB=B*(N-B)
    den=wA+wB
    assert N>=3 and 1<=B<A<=N-1 and den>0
    post=Q(wA,den)
    own=Q(wA*(A-1)+wB*(B-1),(N-2)*den)
    other=Q(wA*B+wB*A,N*den)
    k=A+B-N
    numerator=k*((A+B)*(2*N-A-B)-(2*N-1)*(A-B)**2)
    assert own-other == Q(numerator,2*N*(N-2)*den)
    return post,own,other

print('CHEST: full exhaustive comparison of original and compact criteria, n=3..40')
for N in range(3,41):
    good=[]
    for A in range(2,N):
        for B in range(1,A):
            post,own,other=outcomes(N,A,B)
            criterion=(A+B>N and (A+B)*(2*N-A-B)>(2*N-1)*(A-B)**2)
            assert criterion == (post<Q(1,2) and own>other)
            if criterion: good.append((A,B))
    if N<=10: print(' n=',N,' good=',good)

print('CHEST: disputed individual cases (posterior A, own next G, other next G, gain)')
for N,A,B in [(4,3,2),(5,4,2),(5,4,3),(6,4,3),(6,5,3),(6,5,4)]:
    p,u,v=outcomes(N,A,B)
    print(f' {(N,A,B)}: {p}, {u}, {v}, gain={u-v}')

# Value of first-coin observation given second G, for N=4, A=3, B=2.
# S,G has conditional probability 7/15; G,G has 8/15.
prob_SG=Q(7,15)
prior_opt=Q(3,5)
posterior_opt_SG=Q(5,7)
posterior_opt_GG=Q(9,16)
value=prob_SG*posterior_opt_SG+(1-prob_SG)*posterior_opt_GG-prior_opt
assert value==Q(1,30)
print('CHEST: conditional value of observing first color given G2: ',value)

print('R1: verify five-class N=HEALTHY profiles and pairwise minimum distances')
def profiles(g,e):
    return {
      'N':(1.0,1.0,1.0),
      'L':(g,e,g),
      'W':(e,g,g),
      'E':(e,e,e),
      'LW':(g*e,g*e,g*g),
    }
def mindist(pp,d):
    return min(max(abs(x-y) for x,y in zip(pp[i][:d],pp[j][:d])) for i,j in combinations(pp,2))
for g,e in [(0.9,0.1),(0.7,0.49),(1.0,0.0),(1.0,0.3),(0.8,0.7),(0.5,0.2)]:
    P=profiles(g,e)
    formula_two=min(g-e,e*(1-g))
    formula_three=min(g-e,max(e*(1-g),abs(g*g-e)))
    assert abs(mindist(P,2)-formula_two)<1e-12
    assert abs(mindist(P,3)-formula_three)<1e-12
    print(f' gamma={g:.2f}, eps={e:.2f}: 2-probe gap={formula_two:.6f}, 3-probe gap={formula_three:.6f}')
for gg in range(1,21):
    g=gg/20
    for ee in range(gg):
        e=ee/20
        P=profiles(g,e)
        assert abs(mindist(P,2)-min(g-e,e*(1-g)))<1e-12
        assert abs(mindist(P,3)-min(g-e,max(e*(1-g),abs(g*g-e))))<1e-12
print('R1: all 210 parameter pairs passed both exact separation formulas.')

print('R3: exact McShane-Whitney envelopes for p0(x)=x, L=1 and S={0,1}')
def envelope(p0, L, sites, x):
    upper=min(1, min(p0(t)+L*abs(x-t) for t in sites))
    lower=max(0, max(p0(t)-L*abs(x-t) for t in sites))
    return lower,upper
for i in range(1001):
    x=i/1000
    lo,up=envelope(lambda x:x,1,[0,1],x)
    assert abs(lo-x)<1e-12 and abs(up-x)<1e-12
print('R3: envelopes collapse to identity (exact noiseless theorem).')

eta=0.2; omega=0.05; beta=0.05
m=ceil(2/omega)
G=ceil(12*log(4/beta))
n_conf=ceil(32/eta**2*log(40))
phit=1-exp(-2)
psuccess_lower=phit*0.9*0.95
H1_vote_error=exp(-2*G*(psuccess_lower-0.5)**2)
H0_vote_error=exp(-2*G*(0.5-0.05)**2)
assert H1_vote_error<beta/4 and H0_vote_error<beta/4
print('N2: constructive PAC-group certificate (median elimination itself is a theorem):')
print(f' eta={eta} omega={omega} beta={beta}: group_size={m}, groups={G}, confirm_repeats_per_group={n_conf}')
print(f' prob_detect_per_group>={psuccess_lower:.6f}, upper_H1_vote_error={H1_vote_error:.7f}, upper_H0_vote_error={H0_vote_error:.7f}')
print('N2: this checks the voting arithmetic, not a simulated empirical error rate.')
print('ALL INDEPENDENT CHECKS COMPLETED.')

print('R3: constructive C^1 oscillatory reference, uniform-integral-formula counterexample')
print('    p0=1/2 + box-average[dist(x, (1/K) Z)] with radius delta=1/(100 K^3).')
print('    Slope |p0prime|=1 off at most 4 K delta of [0,1].')
print('    Each of K-1 interior minima supports a disjoint eta-height alternative.')
for K in [10,30,100]:
    delta=Q(1,100*K**3)
    eta=Q(1,10*K)
    int_slack_ub=4*K*delta
    proposed_grid_ub=1+int_slack_ub/eta
    actual_lb=K-1
    assert eta+2*delta < Q(1,K)
    print(f' K={K:3d}: eta={float(eta):.6f}, integral/eta <= {float(int_slack_ub/eta):.6f}, proposed grid surrogate <= {float(proposed_grid_ub):.6f}, actual disjoint alternatives >= {actual_lb}')
