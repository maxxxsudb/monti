#!/usr/bin/env python3
"""Exact finite enumeration of terminal-color protocols and two-box posteriors.

Grammar (NR, sampling uniformly without replacement):
 - each selected box contains n cards, w in {0,..,n} are white;
 - fair coin chooses one of two DIFFERENT compositions, w0 < w1;
 - F: draw exactly k cards (1<=k<=n);
 - W: stop at first white card, or after kth draw;
 - B: stop at first black card, or after kth draw;
 - mandatory photograph of terminal card only, with hidden delay and count;
 - event o=WHITE must have positive probability in BOTH boxes for BOTH protocols.

Two protocols are identified if their likelihood vector over all n+1 compositions
coincides. Changing white vs black globally is not used as an isomorphism:
WHITE is the named observed event, and the target is 'more white cards'.
"""
from fractions import Fraction
from itertools import permutations, combinations
from math import comb
from collections import defaultdict
import argparse

def enum_prob(n, w, mode, k, replace=False):
    colors = (1,)*w + (0,)*(n-w)
    if replace:
        from itertools import product
        paths = product(range(n), repeat=k)
        denom = n**k
    else:
        paths = permutations(range(n), k)
        import math
        denom = math.factorial(n)//math.factorial(n-k)
    win = 0
    for inds in paths:
        last = None
        for i in inds:
            last = colors[i]
            if (mode == 'W' and last == 1) or (mode == 'B' and last == 0):
                break
        if last == 1:
            win += 1
    return Fraction(win, denom)

def closed_prob(n, w, mode, k):
    """Independent combinatorial count (without replacement)."""
    denom=comb(n,k)
    if mode=='F': return Fraction(w,n)
    if mode=='W': return Fraction(denom - (comb(n-w,k) if n-w>=k else 0),denom)
    if mode=='B': return Fraction(comb(w,k) if w>=k else 0,denom)
    raise ValueError(mode)

def verify(nmax=5):
    # Exhaustive ordered-path enumeration must match a completely separate
    # count of unordered subsets, for every n/w/threshold/stop rule.
    checked=0
    for n in range(1,nmax+1):
        for w in range(n+1):
            for k in range(1,n+1):
                for mode in ('F','W','B'):
                    assert enum_prob(n,w,mode,k) == closed_prob(n,w,mode,k), (n,w,mode,k)
                    checked+=1
    assert (enum_prob(3,2,'B',2), enum_prob(3,2,'W',2)) == (Fraction(1,3),Fraction(1))
    assert (enum_prob(5,3,'B',3), enum_prob(5,3,'W',3)) == (Fraction(1,10),Fraction(1))
    # Exactly two draws, random unobserved rule B or W, each p=1/2:
    # AND/OR averaging is equivalent to one uniformly random card.
    for n in range(2,nmax+1):
        for w in range(n+1):
            assert (enum_prob(n,w,'B',2)+enum_prob(n,w,'W',2))/2 == Fraction(w,n)
    print(f'INDEPENDENT CHECK PASSED: {checked} ordered-permutation probabilities matched closed hypergeometric expressions; AND/OR identity checked.')

def list_modes(n, replace=False, maxk=None):
    maxk = maxk or n
    seen = {}
    for k in range(1, maxk+1):
        for mode in ('F','W','B'):
            probs = tuple(enum_prob(n,w,mode,k,replace=replace) for w in range(n+1))
            if probs not in seen:
                seen[probs] = (mode, k)
    return [(name,k,vec) for vec,(name,k) in seen.items()]

def posterior(q0,q1):
    return q1/(q0+q1)

def run(nmax=4, replace=False, maxk=None):
    result={}
    for n in range(1,nmax+1):
        protocols = list_modes(n,replace,maxk)
        examples = []
        num_candidate_pairs = 0
        count_threshold=0
        maxgap=Fraction(0)
        maximizers=[]
        for w0,w1 in combinations(range(n+1),2):
            good=[(mode,k,vec,posterior(vec[w0],vec[w1]))
                  for mode,k,vec in protocols if vec[w0]>0 and vec[w1]>0]
            for x,y in combinations(good,2):
                num_candidate_pairs +=1
                gap=abs(x[3]-y[3]);
                if gap>=Fraction(1,4): count_threshold+=1
                if gap>maxgap:
                    maxgap=gap
                    maximizers=[(w0,w1,x,y)]
                elif gap==maxgap and gap!=0:
                    maximizers.append((w0,w1,x,y))
                examples.append((gap,w0,w1,x,y))
        ex=sorted(examples,key=lambda t:(t[0],-t[1],-t[2]),reverse=True)
        result[n]=(protocols,num_candidate_pairs,count_threshold,maxgap,maximizers,ex)
        print(f'n={n}: unique_protocols={len(protocols)}, candidate_pairs={num_candidate_pairs}, gap>=1/4={count_threshold}, max_gap={maxgap} ({float(maxgap):.6f})')
        for w0,w1,x,y in maximizers[:3]:
            print(f'  max: w0={w0},w1={w1}: {x[0]}{x[1]} -> {x[3]} ({x[2][w0]},{x[2][w1]}); {y[0]}{y[1]} -> {y[3]} ({y[2][w0]},{y[2][w1]})')
    print('\nFIRST THRESHOLD CASES')
    for n in range(1,nmax+1):
        ex=result[n][-1]
        pool=[t for t in ex if t[0]>=Fraction(1,4)]
        if pool:
            for gap,w0,w1,x,y in pool[:12]:
                print(f'n={n}, w0={w0},w1={w1}, {x[0]}{x[1]}={x[3]}, {y[0]}{y[1]}={y[3]}, gap={gap}')
            break
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--max-n',type=int,default=5)
    ap.add_argument('--with-replacement',action='store_true')
    ap.add_argument('--max-k',type=int)
    args=ap.parse_args()
    if not args.with_replacement:
        verify(args.max_n)
    run(args.max_n,args.with_replacement,args.max_k)
