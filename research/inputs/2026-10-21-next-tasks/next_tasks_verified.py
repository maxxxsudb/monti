#!/usr/bin/env python3
"""Reproducible math and synthetic checks for HARD-TASKS-NEXT (21 Oct 2026).
Requires numpy and scipy for independent optimization checks.
All human-behavior data below are synthetic, not participant responses.
"""
from math import sqrt, log, ceil, comb
from fractions import Fraction as F
import numpy as np
from numpy.linalg import inv, norm
from scipy.optimize import differential_evolution, minimize, linprog, minimize_scalar

rng=np.random.default_rng(20261021)
def f(x): return 2*np.asarray(x)/(1+np.asarray(x))
def D(x):
 x=np.asarray(x,dtype=float); u=f(x)
 return np.column_stack([x-u, .5-u, 2/3-u])
def nodes(lo,hi): return np.array([lo,sqrt((1+lo)*(1+hi))-1,hi])
def lambdastar(lo,hi): return 2/(sqrt(1+hi)-sqrt(1+lo))**2

def T(x,t):
 x=np.asarray(x,dtype=float); t=np.asarray(t,dtype=float)
 a=[]
 for i in range(3):
  j,k=[m for m in range(3) if m!=i]
  a.append((1+x[i])/(1+t)*(t-x[j])*(t-x[k])/((x[i]-x[j])*(x[i]-x[k])))
 return np.stack(a,axis=-1)
def coefnorm(x):
 x=np.sort(x)
 if min(np.diff(x))<1e-9: return 1e12
 return np.max(np.sum(np.abs(inv(D(x))),axis=1))
def prednorm(x):
 x=np.sort(x)
 if min(np.diff(x))<1e-9: return 1e12
 return np.max(np.sum(np.abs(T(x,np.linspace(0,1,4001))),axis=1))

def test_design(lo,hi):
 x=nodes(lo,hi); A=inv(D(x)); grid=np.linspace(0,1,6001)
 pc=np.max(np.sum(np.abs(T(x,grid)),axis=1))
 row=np.sum(np.abs(A),axis=1)
 resC=differential_evolution(coefnorm,[(lo,hi)]*3,tol=5e-10,seed=4,popsize=14,maxiter=300,polish=True)
 resP=differential_evolution(prednorm,[(lo,hi)]*3,tol=1e-8,seed=5,popsize=10,maxiter=180,polish=True)
 print(f'DESIGN [{lo:.1f},{hi:.1f}] nodes={x.tolist()}')
 print(f'  coefficient inverse row sums={row.tolist()}, OPT=2/(sqrt(1+hi)-sqrt(1+lo))^2={lambdastar(lo,hi):.12f}, optimized={resC.fun:.12f}')
 print(f'  prediction sup Lebesgue={pc:.12f}, optimized sampled={resP.fun:.12f}, numerical optimizer nodes={sorted(resP.x)}')
 assert abs(row.max()-lambdastar(lo,hi))<1e-7
 assert abs(coefnorm(x)-resC.fun)<1e-5
 assert abs(pc-resP.fun)<3e-5
 return x,pc

x0,l0=test_design(0,1)
x1,l1=test_design(.1,.9)
print('BASELINE nodes=[0,.25,.5], coefficient norm=',coefnorm([0,.25,.5]),' prediction norm=',prednorm([0,.25,.5]))
print('CONSTRAINED prediction exact 1+0.09*coefnorm=',1+.09*lambdastar(.1,.9))
# Function reconstruction exact rational arithmetic at 0,1/4,1/2
la=[F(1,4),F(1,5),F(1,10)]
def pfrac(x):
 ff=2*x/(1+x)
 return ff+la[0]*(x-ff)+la[1]*(F(1,2)-ff)+la[2]*(F(2,3)-ff)
for z in (F(0),F(1,4),F(1,2),F(1,5),F(3,8),F(3,4)):
 print('EXACT-EXAMPLE',str(z),'p=',str(pfrac(z)),'decimal=',float(pfrac(z)))
print('SIMPLIFIED λ=',list(map(str,la)),'sum=',sum(la))
# finite holdout variance-optimal allocations
hold=np.array([.2,.375,.75]); W=T(x0,hold)

def alloc_obj(fr): return np.max(np.sum(W*W/fr[None,:],axis=1))
res=minimize(alloc_obj,np.array([1/3]*3),method='SLSQP',bounds=[(.005,.99)]*3,constraints=[{'type':'eq','fun':lambda z:np.sum(z)-1}],options={'ftol':1e-13,'maxiter':1000})
print('ALLOCATION holdouts:', hold.tolist(),'W:',np.round(W,8).tolist())
print('ALLOCATION minimax fractions=',res.x.tolist(),'worst N*varianceproxy=',res.fun,'equal=',alloc_obj(np.array([1/3]*3)))
# Dual KKT certificate for convex minimax allocation.
U=W*W
def dualfun(pi): return np.sum(np.sqrt(pi@U))**2
rdual=minimize(lambda p:-dualfun(p),[1/3]*3,method='SLSQP',bounds=[(0,1)]*3,constraints=[{'type':'eq','fun':lambda p:sum(p)-1}],options={'ftol':1e-14,'maxiter':3000})
pi=rdual.x
z=np.sqrt(pi@U); ac=z/sum(z)
vals=np.sum(U/ac[None,:],axis=1)
dual=dualfun(pi)
print('ALLOCATION dual certificate pi=',pi.tolist(),'fractions=',ac.tolist(),'primal individual objectives=',vals.tolist(),'dual value=',dual,'gap=',max(vals)-dual)
assert abs(max(vals)-dual)<1e-7
# Bernoulli synthetic training and held-out validation
n=1500; yy=[]
for xx in x0:
 q=float(f(xx)+D([xx])[0] @ np.asarray(la,dtype=float)); yy.append(float(rng.binomial(n,q)/n))
lamhat=inv(D(x0))@(np.asarray(yy)-f(x0))
for z in hold:
 true=float(pfrac(F(str(z))))
 pred=float(f(z)+D([z])[0]@lamhat)
 v=float(T(x0,z)@np.asarray(yy)) # NB: this interpolates p, not residual! p is NOT in span residuals.
 yyf=np.asarray(yy)-f(x0)
 pred2=float(f(z)+T(x0,z)@yyf)
 assert abs(pred-pred2)<1e-10
 nn=600; observed=float(rng.binomial(nn,true)/nn)
 print('SYNTH-HOLDOUT',f'alpha={z}, predicted={pred:.7f}, truth={true:.7f}, heldout_mean={observed:.7f}')
print('SYNTH fitted lambda=',lamhat.tolist(),'in simplex=',bool(np.all(lamhat>=0) and sum(lamhat)<=1))

# Honest confidence polytope: guaranteed coverage under bounded iid responses.
conf_beta=.05; eps_obs=sqrt(log(6/conf_beta)/(2*n))
train_delta=np.asarray(yy)-f(x0)
A_ub=np.vstack([D(x0),-D(x0),np.ones((1,3))])
b_ub=np.r_[train_delta+eps_obs,-train_delta+eps_obs,1.]
fit=linprog([0.,0.,0.],A_ub=A_ub,b_ub=b_ub,bounds=[(0,None)]*3,method='highs')
print('CONFIDENCE train n_each=',n,'beta=',conf_beta,'Hoeffding radius=',eps_obs,'polytope feasible=',fit.success)
assert fit.success
for z in hold:
 row=D([z])[0]; lo=linprog(row,A_ub=A_ub,b_ub=b_ub,bounds=[(0,None)]*3,method='highs'); hi=linprog(-row,A_ub=A_ub,b_ub=b_ub,bounds=[(0,None)]*3,method='highs')
 assert lo.success and hi.success
 low=float(f(z)+lo.fun); high=float(f(z)-hi.fun)
 assert low-1e-8<=float(pfrac(F(str(z))))<=high+1e-8
 print('CONFIDENCE-HOLDOUT',z,'prediction_band=',(round(low,7),round(high,7)))

# training+independent-validation worst-case Hoeffding budget
beta=.05;eta=.2;omega=.2
nt=ceil(32*l0*l0/eta**2*log(18/beta))
M=ceil(log(3/beta)/(-log(1-omega)))
sv=ceil(8/eta**2*log(6*M/beta))
print('UNKNOWN-GUARANTEE beta eta omega=',beta,eta,omega,'n_train_each=',nt,'M_validation_points=',M,'n_each_validation=',sv,'total=',3*nt+M*sv)

# End-to-end independent split test under a known catalog member (Bernoulli mean 1/2).
def fit_catalog_minimax(nodes, empirical):
 mat=D(nodes)
 # Variables = [lambda_P,lambda_E,lambda_C,t], minimize t.
 rows=np.vstack([np.column_stack([mat,-np.ones(3)]),np.column_stack([-mat,-np.ones(3)]),np.array([[1.,1.,1.,0.]])])
 bounds=np.r_[empirical-f(nodes),-empirical+f(nodes),1.]
 fit=linprog([0.,0.,0.,1.],A_ub=rows,b_ub=bounds,bounds=[(0,None)]*4,method='highs')
 assert fit.success
 return fit.x[:3]
train_means=np.array([rng.binomial(nt,.5)/nt for xx in x0])
qhat=fit_catalog_minimax(x0,train_means)
Xval=rng.random(M)
meansval=np.array([rng.binomial(sv,.5)/sv for xx in Xval])
diffs=np.abs(meansval-f(Xval)-D(Xval)@qhat)
print('UNKNOWN-SYNTH-NULL fitted lambda=',qhat.tolist(),'max_validation_deviation=',float(max(diffs)),'threshold=',5*eta/8,'decision=',('UNKNOWN' if any(diffs>5*eta/8) else 'CATALOG'))
# attack family proof constant calculation (three separated anchor bands)
K=2*(1/(.28*.84)+1/(.28*.48)+1/(.48*.84))
print('ATTACK uniform interpolation upper K=',K,'height H=32eta, feasible if eta<=1/128, omega<=0.05')
assert K<31
# explicit family J width 2ω, flat center width ω, avoiding anchors and training design
omega2=.02;eta2=.005
supports=[]
for lo,hi in ((.10,.34),(.46,.90)):
 for k in range(int((hi-lo)/(2*omega2))): supports.append((lo+2*omega2*k, lo+2*omega2*(k+1)))
def attack(z,I):
 a,b=I; d=omega2/2
 # width support=2omega, plateau central omega
 if z<a or z>b:return .5
 if z<a+d:return .5+32*eta2*(z-a)/d
 if z<=b-d:return .5+32*eta2
 return .5+32*eta2*(b-z)/d
for I in supports:
 for xx in x0: assert abs(attack(xx,I)-.5)<1e-10
 for z in [I[0]+.75*omega2, I[0]+omega2,I[0]+1.25*omega2]: assert abs(attack(z,I)-.5-32*eta2)<1e-10
print('ATTACK-FAMILY count=',len(supports),'omega=',omega2,'eta=',eta2,'all match training nodes; each is UNKNOWN relative to every simplex function by anchor/interpolation lemma')

# Numerical audit of all 17 locations and a grid of catalogue parameters.
probegrid=np.linspace(0,1,2001)
mesh=[]
for vP in np.linspace(0,1,11):
 for vE in np.linspace(0,1-vP,11):
  for vC in np.linspace(0,1-vP-vE,11): mesh.append([vP,vE,vC])
mesh=np.asarray(mesh)
qgrid=f(probegrid)[None,:]+mesh@D(probegrid).T
min_fraction=1.
for I in supports:
 avec=np.array([attack(t,I) for t in probegrid])
 fr=np.mean(np.abs(qgrid-avec[None,:])>=eta2,axis=1)
 min_fraction=min(min_fraction,float(fr.min()))
print('ATTACK-FAMILY grid catalogue audit min disagreement fraction=',min_fraction,'required omega=',omega2,'(grid check only; universal guarantee is analytic)')
print('ALL CHECKS PASSED')
