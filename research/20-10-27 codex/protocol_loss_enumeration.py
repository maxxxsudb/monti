#!/usr/bin/env python3
"""Exact exhaustive finite search for the protocol-loss urn task.

Scope G(n): two possible urn compositions with equal prior, 1<=wL<wH<=n;
shuffle uniformly, draw without replacement; stop after k, at the first white,
or at the first black, whichever first. Photograph the FINAL draw only.
Neither the earlier colors nor the number of draws is disclosed.
All fractions are exact. No external dependencies.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
from math import comb

FIXED, FIRST_WHITE, FIRST_BLACK = 'F', 'W', 'B'

def protocols(n):
    return [(t,k) for k in range(1,n+1) for t in (FIXED,FIRST_WHITE,FIRST_BLACK)]

def photo_white_order(colors, rule):
    t,k=rule
    last=None
    for j in range(k):
        last=colors[j]
        if t == FIRST_WHITE and last==1: break
        if t == FIRST_BLACK and last==0: break
    return last == 1

def likelihood_bruteforce(n,w,rule):
    # Every length-n binary ordering with w whites is equiprobable.
    positives=0
    for spots in combinations(range(n), w):
        white=set(spots)
        colors=tuple(int(j in white) for j in range(n))
        positives+=int(photo_white_order(colors,rule))
    return F(positives, comb(n,w))

def likelihood_formula(n,w,rule):
    kind,k=rule
    if kind == FIXED: return F(w,n)
    if kind == FIRST_WHITE:
        return 1-F(comb(n-w,k) if k <= n-w else 0, comb(n,k))
    if kind == FIRST_BLACK:
        return F(comb(w,k) if k <= w else 0, comb(n,k))
    raise ValueError(rule)

def posterior(white_low,white_high,prior=F(1,2)):
    assert white_low>0 and white_high>0 and 0<prior<1
    return prior*white_high / (prior*white_high+(1-prior)*white_low)

def scan(n,verbose=False):
    total_raw=0
    valid_raw=0
    raw_pairs=0
    canonical_protocols=0
    canonical_pairs=0
    all_pairs=[]
    one_word=[]
    maxgap=F(0)
    examples=[]
    for wl in range(1,n):
        for wh in range(wl+1,n+1):
            kernels=defaultdict(list)
            for rule in protocols(n):
                total_raw+=1
                x=likelihood_bruteforce(n,wl,rule)
                y=likelihood_bruteforce(n,wh,rule)
                assert x==likelihood_formula(n,wl,rule)
                assert y==likelihood_formula(n,wh,rule)
                if x==0 or y==0:
                    continue # Both hypotheses must be capable of producing white.
                valid_raw+=1
                kernels[(x,y)].append(rule)
            sigs=sorted(kernels)
            canonical_protocols+=len(sigs)
            raw_pairs+=comb(sum(map(len,kernels.values())),2)
            for a,b in combinations(sigs,2):
                canonical_pairs+=1
                gap=abs(posterior(*a)-posterior(*b))
                if gap>maxgap: maxgap=gap
                all_pairs.append((gap,wl,wh,a,b,kernels[a],kernels[b]))
            for k in range(1,n+1):
                a=(likelihood_formula(n,wl,(FIRST_WHITE,k)), likelihood_formula(n,wh,(FIRST_WHITE,k)))
                b=(likelihood_formula(n,wl,(FIRST_BLACK,k)), likelihood_formula(n,wh,(FIRST_BLACK,k)))
                if 0 in a or 0 in b:continue
                gap=abs(posterior(*a)-posterior(*b))
                if gap:
                    one_word.append((gap,wl,wh,k,a,b,posterior(*a),posterior(*b)))
    all_pairs.sort(reverse=True)
    one_word.sort(reverse=True)
    print(f'n={n}: compositions={comb(n,2)} raw_protocols={total_raw} valid_protocols={valid_raw} raw_valid_pairs={raw_pairs} canonical_protocols={canonical_protocols} canonical_pairs={canonical_pairs} max_gap={maxgap} ({float(maxgap):.8f})')
    if one_word:
        g,wl,wh,k,a,b,pa,pb=one_word[0]
        print(f'   best SAME-k W/B stop switch: low={wl}W high={wh}W k={k}: gap={g} ({float(g):.8f}); postW={pa}, postB={pb}')
    if verbose:
        print('   top distinct-idea pairs:')
        for gap,wl,wh,a,b,ra,rb in all_pairs[:8]:
            print(f'     {wl}W vs {wh}W: gap={gap}, post={posterior(*a)}/{posterior(*b)} kernels={a}/{b}, rules={ra}/{rb}')
    return all_pairs,one_word

def validate_general_theorem():
    # Algebraic criterion checked on 3-state example vectors of nonnegative integers.
    from itertools import product
    ys=(0,0,1)
    vecs=[v for v in product(range(3),repeat=3) if any(v)]
    priors=[(F(1,3),F(1,3),F(1,3)),(F(1,6),F(1,3),F(1,2)),(F(1,2),F(1,4),F(1,4))]
    total=0
    for a in vecs:
        for b in vecs:
            cross=all(a[s]*b[t]==b[s]*a[t] for s in range(3) for t in range(3) if ys[s]!=ys[t])
            support_layer={ys[i] for i in range(3) if a[i] or b[i]}
            proportional=all(a[i]*b[j]==a[j]*b[i] for i in range(3) for j in range(3))
            structural=proportional or len(support_layer)==1
            assert cross==structural,(a,b)
            if cross:
                for mu in priors:
                    A=sum(mu[i]*a[i] for i in range(3))
                    B=sum(mu[i]*b[i] for i in range(3))
                    assert sum(mu[i]*a[i] for i in range(2))/A==sum(mu[i]*b[i] for i in range(2))/B
            total+=1
    print(f'universal likelihood-ratio criterion: {total} exhaustive integer-vector pairs tested')

def n7_extra():
    # Restrict to two draws, stopping on the FIRST WHITE versus FIRST BLACK;
    # require both report colors possible under both types and both protocols.
    for n in range(2,12):
        candidates=[]
        for lo in range(1,n):
            for hi in range(lo+1,n+1):
                a=[likelihood_formula(n,w,(FIRST_WHITE,2)) for w in (lo,hi)]
                b=[likelihood_formula(n,w,(FIRST_BLACK,2)) for w in (lo,hi)]
                if not all(0<x<1 for x in a+b):continue
                pa=posterior(*a)
                pb=posterior(*b)
                delta=abs(pa-pb)
                if delta>=F(1,4): candidates.append((delta,lo,hi,pa,pb,a,b))
        if candidates:
            candidates.sort(reverse=True)
            print('first all-four-likelihoods-strictly-between-0-and-1 with gap>=1/4: n=',n,'best=',candidates[0])
            return n,candidates[0]
    raise AssertionError('no nondegenerate example found')

def main():
    validate_general_theorem()
    for n in (2,3,4):
        scan(n,verbose=n==3)
    print('\nChosen n=3 construction: 2W+1B versus 3W:')
    for rule in ((FIRST_WHITE,2),(FIRST_BLACK,2)):
        lw=likelihood_bruteforce(3,2,rule)
        hw=likelihood_bruteforce(3,3,rule)
        print(f'   rule={rule}, likelihood_low={lw}, likelihood_high={hw}, posterior={posterior(lw,hw)}')
    assert posterior(F(1),F(1))==F(1,2)
    assert posterior(F(1,3),F(1))==F(3,4)
    assert F(1,2)<F(5,8)<F(3,4)
    n7_extra()
    r=F(1,2) # Prior probability that first-black protocol was used.
    wrong_naive=(1-r)*F(1,2)+r*F(3,4)
    correct=1 / (2 - F(2,3)*r)
    posterior_B_given_white = (r*F(2,3))/((1-r)*1 + r*F(2,3))
    print(f'unknown protocol prior(B)=1/2: naive mean posterior={wrong_naive}, correct posterior={correct}, P(B|photo_white)={posterior_B_given_white}')
    print('photo-label symmetric noise:')
    for eta in (F(0),F(1,10),F(1,4),F(2,7),F(1,2)):
        pA=F(1,2)
        pB=F(3)*(1-eta)/(4-2*eta)
        print('   eta=',eta,' pA=',pA,' pB=',pB,' delta=',pB-pA,' buy_B_at_5/8=',pB>F(5,8))
    print('PASS: all exact checks')

if __name__=='__main__':
    main()
