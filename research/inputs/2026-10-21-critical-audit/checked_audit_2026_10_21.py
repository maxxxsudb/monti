#!/usr/bin/env python3
"""Exact, pure-stdlib verification of the October 21 critical audit.
Run: python checked_audit_2026_10_21.py
All finite calculations use fractions.Fraction, not Monte Carlo or floats.
"""
from fractions import Fraction as F
from itertools import product
from math import comb


def pmf(k, p, n=3):
    return F(comb(n, k))*p**k*(1-p)**(n-k)


def exact_minimax_certificate():
    names = ('N','L','W','E','LW')
    ps = {
        'N': (F(1),)*3,
        'L': (F(9,10),F(1,10),F(1,10)),
        'W': (F(1,10),F(9,10),F(1,10)),
        'E': (F(1,10),F(1,10),F(9,10)),
        'LW': (F(9,100),F(9,100),F(1,100))
    }
    def prob(name, v):
        out=F(1)
        for k,p in zip(v,ps[name]):out *= pmf(k,p)
        return out
    ratio=F(91273273091,729000000000)
    a=F(729,1000000000)
    z=1/(1+3*ratio+a*ratio)
    y=ratio*z
    prior={'N':a*y,'L':y,'W':y,'E':y,'LW':z}
    assert sum(prior.values())==1
    rand={
        (0,2,0):('W','LW',F(166772659224244268732865365,177646534311799495515253833)),
        (2,0,0):('L','LW',F(159310463205922869055269013,177646534311799495515253833)),
        (3,0,3):('L','E',F(611976287197017606944062,731055696756376524754131)),
        (3,3,3):('N','W',F(319970344592073815640,334273295270405361113))
    }
    tie_override={(2,2,2):'W',(3,3,0):'W',(3,3,1):'W'}
    risks={name:F(1) for name in names}
    bayes_correct=F(0)
    for v in product(range(4),repeat=3):
        weights={name:prior[name]*prob(name,v) for name in names}
        bayes_correct+=max(weights.values())
        winners=[k for k in names if weights[k]==max(weights.values())]
        if v in rand:
            first,second,u=rand[v]
            assert 0<=u<=1
            assert first in winners and second in winners
            decision={first:u,second:1-u}
        else:
            pick=tie_override.get(v,winners[0])
            assert pick in winners
            decision={pick:F(1)}
        for name,prob_pick in decision.items():
            risks[name]-=prob(name,v)*prob_pick
    value=F(14302950678331545473,334273295270405361113)
    assert set(risks.values())=={value}
    assert 1-bayes_correct==value
    assert value!=F(557,13000)
    print('CALIBRATED MINIMAX: EXACT:',value,'= %.12f'%float(value))
    print('Claimed 557/13000:',F(557,13000),'= %.12f'%float(F(557,13000)))
    print('Five exact risks:', ', '.join('%s=%s'%(key,risks[key]) for key in names))
    print('Exact primal and least-favorable-prior dual certificates: PASS')


def like(n,w,k):
    C=comb(n,k)
    black=comb(n-w,k) if k<=n-w else 0
    allwhite=comb(w,k) if k<=w else 0
    return F(allwhite,C), F(C-black,C)


def formula(n):
    if n%2:
        m=(n+1)//2; C=comb(n,m)
        return F(C-1,2*(C+1))
    m=n//2;C=comb(n,m);Cp=comb(n,m+1)
    center=F(C*(C-2),(C+1)*(2*C-1))
    shift=F(Cp-1,2*(Cp+1))
    return max(center,shift)


def global_box_check(max_n=22):
    print('GLOBAL BOX CHECK over all 1<=w_low<w_high<=n, 1<=k<=n; require both observed white likelihoods > 0')
    for n in range(3,max_n+1):
        best=F(-1);arg=[]
        for k in range(1,n+1):
            for low in range(1,n):
                qlow, rlow=like(n,low,k)
                if not qlow or not rlow: continue
                for high in range(low+1,n+1):
                    qhi,rhi=like(n,high,k)
                    if not qhi or not rhi:continue
                    d=abs(qhi/(qhi+qlow)-rhi/(rhi+rlow))
                    if d>best:best=d;arg=[(low,high,k)]
                    elif d==best:arg.append((low,high,k))
        assert best==formula(n),(n,best,formula(n),arg)
        if n in (3,4,5,6,7,8,10,12,16,22):
            print('n=%d: max=%s | optimizers=%s | PASS'%(n,best,arg))
    print('GLOBAL BOX CHECK: ALL PASS for n=3..%d'%max_n)
    for m in (2,3,4,5,10):
        C=comb(2*m,m);Cp=comb(2*m,m+1)
        center=F(C*(C-2),(C+1)*(2*C-1))
        shift=F(Cp-1,2*(Cp+1))
        deficit=F(1,2)-center
        assert deficit == F(5*C-1,2*(C+1)*(2*C-1))
        sign=(m-4)*C*C+(2*m+3)*C+(m+1)
        assert (shift>center)==(sign>0)
        print('even n=%d center=%s shift=%s winner=%s'%(2*m,center,shift,'shift' if sign>0 else 'center'))


def five_class_profiles():
    eps=F(1,10)
    sets={'N':(), 'L':(0,), 'W':(1,), 'E':(2,), 'LW':(0,1)}
    sig={}
    for name,B in sets.items():
        values=[]
        for j in range(3):
            p=F(1)
            for d in B:p*=1-eps if d==j else eps
            values.append(p)
        sig[name]=tuple(values)
    assert len(set(sig.values()))==5
    assert sig['LW']==(F(9,100),F(9,100),F(1,100))
    # High/low mechanism classifications, as in the original five-class proof.
    bits={name:tuple(int(p>F(1,2)) for p in row) for name,row in sig.items()}
    assert len(set(bits.values()))==5
    print('FIVE-CLASS SIGNALS:')
    for name in sets:print(name, sig[name],bits[name])
    print('FIVE-CLASS 3-SINGLETON SIGNATURES: PASS')


if __name__=='__main__':
    five_class_profiles()
    exact_minimax_certificate()
    global_box_check()
