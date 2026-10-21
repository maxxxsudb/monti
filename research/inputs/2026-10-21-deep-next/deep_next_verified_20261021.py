#!/usr/bin/env python3
"""Reproducible independent verification of new limited-class results (2026-10-21).
Requires numpy for synthetic paired Bernoulli observations. All real-human data absent.
"""
import math
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
rng=np.random.default_rng(20261021)

def f(x): return 2*x/(1+x)
def d(x): return np.asarray([x-f(x),.5-f(x),2/3-f(x)])
def D(nodes): return np.stack([d(x) for x in nodes])
def weights(nodes,x):
    return np.asarray([(1+nodes[i])/(1+x)*np.prod([(x-nodes[j])/(nodes[i]-nodes[j]) for j in range(3) if j!=i]) for i in range(3)])

print('N1 analytic checkpoints')
b=math.sqrt(2)-1
M=D([0,b,1]); inv=np.linalg.inv(M)
print(' optimal nodes=',[0,b,1],'inv_norm=',np.abs(inv).sum(axis=1).max())
assert abs(np.abs(inv).sum(axis=1).max()-(6+4*math.sqrt(2)))<1e-10
x=np.linspace(0,1,10001)
assert max(np.sum(weights([0,b,1],t)**2) for t in x) <=1+1e-12
print(' sum(T_i^2) max =', max(np.sum(weights([0,b,1],t)**2) for t in x))
print('\nINSIGHT1 detection-only optimization')
a=F(2,3)
print(' alpha=2/3 correct=',F(4,5),'heuristic values=',a,F(1,2),F(2,3),'gap=',F(2,15))
assert F(4,5)-max(a,F(1,2),F(2,3))==F(2,15)
# Convex discrepancy d_B for constant wrong weights by LP, with node alpha=2/3
for nodes in [[2/3],[2/3,b],[0,b,2/3,1]]:
    # min r s.t. -r <= D w <=r ; sum w=1, w>=0
    mat=D(nodes)
    Aub=[]; bub=[]
    for row in mat:
        Aub.append(np.r_[row,-1]); bub.append(0)
        Aub.append(np.r_[-row,-1]); bub.append(0)
    solution=linprog([0,0,0,1],A_ub=Aub,b_ub=bub,A_eq=[[1,1,1,0]],b_eq=[1],bounds=[(0,None)]*4,method='highs')
    assert solution.success
    print(' battery=',[round(v,6) for v in nodes],'gap=',round(solution.x[3],9),'min_weight=',solution.x[:3].round(5).tolist())

print('\nINSIGHT1 new globally optimal TWO-point detection battery')
from scipy.optimize import linprog as _lp
t=2-math.sqrt(2)
gstar=(18-8*math.sqrt(2))/49
wstar=(22+12*math.sqrt(2))/49
for pts in ([0,t],np.linspace(0,1,401)):
    mat=D(pts);au=[];bu=[]
    for row in mat:
        au.append(np.r_[row,-1]);bu.append(0)
        au.append(np.r_[-row,-1]);bu.append(0)
    sol=_lp([0,0,0,1],A_ub=au,b_ub=bu,A_eq=[[1,1,1,0]],b_eq=[1],bounds=[(0,None)]*4,method='highs')
    assert sol.success
    print(' points=',len(pts),'gap=',round(sol.x[3],12),'weights=',sol.x[:3].round(7).tolist())
    assert abs(sol.x[3]-gstar)<2e-5
print(' exact optimum gap=',gstar,'pure mix prior=',wstar,'classic=',1-wstar)
assert abs(max(abs(wstar*xx+(1-wstar)*2/3 - f(xx)) for xx in np.linspace(0,1,10001))-gstar)<5e-8

print('\nINSIGHT2 four variants exact posterior')
for prior in [F(1,2), F(1,3)]:
    for r_ordinary in [F(2,5),F(1,5)]:
        lr=F(4,5)/r_ordinary
        posterior=prior*lr/(1-prior+prior*lr)
        print(' prior=',str(prior),'ordinary_red=',str(r_ordinary),'LR=',str(lr),'posterior=',str(posterior))

print('\nINSIGHT3 varying weights is outside constant catalog but decision robust')
# p=f+lambdaP*dP + lambdaE*dE + lambdaC*dC, lambdaE variable
nodes=[0,b,1]
lam0=np.array([.2,.2,.2]);
def p_nonconstant(xx):
    lam=lam0+np.array([0,.1*xx*(1-xx),0]);return f(xx)+np.dot(lam,d(xx))
train=np.array([p_nonconstant(t) for t in nodes])
lam_est=np.linalg.solve(D(nodes),train-np.array([f(t) for t in nodes]))
validation=.8
pred=f(validation)+weights(nodes,validation)@(train-np.array([f(t) for t in nodes]))
truth=p_nonconstant(validation)
print(' inferred constant lambda=',lam_est.round(8),'sum=',lam_est.sum())
print(' holdout alpha=.8 predicted=',pred,'actual=',truth,'difference=',abs(pred-truth))
assert np.min(lam_est)>0 and lam_est.sum()<1 and abs(pred-truth)>0.00001
print(' threshold .65: both say', ('HIGH' if pred>.65 else 'LOW'))

print('\nINSIGHT4 latent persistence and learning simulation')
n=150000
lam=.4;kappa=.65;learn=.07
xx=.10;yy=.20
dx=2/3-f(xx);dy=2/3-f(yy)
h1=(rng.random(n)<lam).astype(int)
p2=(1-kappa)*lam+kappa*h1+learn
assert np.all((p2>=0)&(p2<=1))
h2=(rng.random(n)<p2).astype(int)
a1=(rng.random(n)<(f(xx)+h1*dx)).astype(float)
a2=(rng.random(n)<(f(yy)+h2*dy)).astype(float)
C=np.mean((a1-a1.mean())*(a2-a2.mean()))
Cexp=lam*(1-lam)*kappa*dx*dy
ell_hat=(a2.mean()-f(yy))/dy-lam
kap_hat=C/(lam*(1-lam)*dx*dy)
print(' expected covariance=',round(Cexp,8),'measured=',round(C,8))
print(' true kappa=',kappa,'estimated=',round(kap_hat,4),'true learning=',learn,'estimated=',round(ell_hat,4))
assert abs(C-Cexp)<.01 and abs(ell_hat-learn)<.03

# Pac median elimination routine using binomial sampling of means for signed arms.
def median_elimination(pvals, qvals, arm_eps, delta=.05):
    active=list(range(2*len(pvals)))
    eps=arm_eps/4.;dl=delta/2.;tot=0
    while len(active)>1:
        nn=math.ceil(2/(eps*eps)*math.log(5/dl))
        scores=[]
        for i in active:
            x=i//2;s=1 if i%2==0 else -1
            successes=rng.binomial(nn,pvals[x]);tot+=nn
            reward=.5*(1+s*(successes/nn-qvals[x]))
            scores.append(reward)
        keep=(len(active)+1)//2
        order=np.argsort(scores)[-keep:]
        active=[active[k] for k in order]
        eps*=.75;dl*=.5
    return active[0],tot

def trial_block_unknown(eta=.4,omega=.2,alternative=True):
    M0=math.ceil(math.log(20)/omega)
    xx=rng.random(M0)
    q=np.full(M0,.5)
    p=q.copy()
    if alternative:p[xx<omega]=.5+eta
    chosen,total=median_elimination(p,q,eta/8.,delta=.05)
    idx=chosen//2;sg=1 if chosen%2==0 else -1
    confirm=math.ceil(32/(eta*eta)*math.log(20))
    count=rng.binomial(confirm,p[idx]);total+=confirm
    score=.5*(1+sg*(count/confirm-q[idx]))
    return score>.5+eta/4,total
print('\nN2 explicit alternating continuous UNKNOWN attack, finite grid sanity')
eta=.15;omega=.005; grid=np.linspace(0,1,100001)
pert=np.zeros_like(grid)
start=.1
for ii in range(8):
    sign=1 if ii%2==0 else -1
    left=start+ii*3*omega/4
    ramp=omega/8
    plat=omega/2
    mid1=left+ramp;mid2=mid1+plat;right=mid2+ramp
    aa=(grid>=left)&(grid<mid1);bb=(grid>=mid1)&(grid<=mid2);cc=(grid>mid2)&(grid<=right)
    pert[aa]=sign*eta*(grid[aa]-left)/ramp
    pert[bb]=sign*eta
    pert[cc]=sign*eta*(right-grid[cc])/ramp
attack=.5+pert
assert min(attack)>.25 and max(attack)<.75
for x0 in [0,math.sqrt(2)-1,1,.4]:
    assert abs(attack[np.argmin(abs(grid-x0))]-.5)<1e-12
rng2=np.random.default_rng(17)
minimum=1.
for j in range(150):
    v=rng2.dirichlet(np.ones(4))
    qq=2*grid/(1+grid)+v[0]*(grid-2*grid/(1+grid))+v[1]*(.5-2*grid/(1+grid))+v[2]*(2/3-2*grid/(1+grid))
    meas=np.mean(np.abs(attack-qq)>=eta-1e-10)
    minimum=min(minimum,meas)
print(' height=',eta,'omega=',omega,'least measured violating set over 150 random q=',round(minimum,6))
assert minimum>=omega-0.00002

print('\nN2 PAC median-elimination sanity test (catalog q=.5 known, toy wide alternative)')
for hyp in (False,True):
    successes=0; costs=[]
    for i in range(24):
        outcome,cost=trial_block_unknown(alternative=hyp);successes+=outcome;costs.append(cost)
    print(' alternative=',hyp,'positive blocks=',successes,'/24','samples/block=',costs[0])
    if hyp:assert successes>=15
    else:assert successes<=7
print('\nVERIFIED: all script assertions passed. Simulations are synthetic, not human observations.')
