import itertools, numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
def solve(pi, strong=True, margin=0.0, sizes=None):
    """max E TV(true, CAR-naive) over truthful protocols s.t. naive argmax is truly optimal on each message.
    margin: require x_top >= x_theta + margin*x(S)?  (true posterior margin) -- 0 = weak ties allowed."""
    n=len(pi); pi=np.array(pi,float)
    msgs=[S for k in range(2,n+1) for S in itertools.combinations(range(n),k) if sizes is None or k in sizes]
    # variables: x[S,θ] (mass), u[S,θ] (positive part), z[S,θ] binary
    idx={}; c=0
    for S in msgs:
        for t in S: idx[('x',S,t)]=c; c+=1
    for S in msgs:
        for t in S: idx[('u',S,t)]=c; c+=1
    for S in msgs:
        for t in S: idx[('z',S,t)]=c; c+=1
    nv=c; obj=np.zeros(nv); integ=np.zeros(nv); lb=np.zeros(nv); ub=np.ones(nv)
    for S in msgs:
        for t in S: obj[idx[('u',S,t)]]=-1; integ[idx[('z',S,t)]]=1
    A=[];lo=[];hi=[]
    for th in range(n):   # mass budget
        row=np.zeros(nv)
        for S in msgs:
            if th in S: row[idx[('x',S,th)]]=1
        A.append(row); lo.append(0); hi.append(pi[th])
    for S in msgs:
        piS=sum(pi[list(S)]); top=max(S,key=lambda t:pi[t])
        tops=[t for t in S if abs(pi[t]-pi[top])<1e-12]
        for m in (tops if strong else [top]):
            for t in S:
                if t==m: continue
                row=np.zeros(nv); row[idx[('x',S,m)]]=1; row[idx[('x',S,t)]]=-1
                for s2 in S: row[idx[('x',S,s2)]]-=margin
                A.append(row); lo.append(0); hi.append(np.inf)
        for t in S:
            # u <= naive_t * x(S) - x_t + (1-z)   ;  u <= z
            row=np.zeros(nv); row[idx[('u',S,t)]]=1
            for s2 in S: row[idx[('x',S,s2)]]-=pi[t]/piS
            row[idx[('x',S,t)]]+=1; row[idx[('z',S,t)]]+=1
            A.append(row); lo.append(-np.inf); hi.append(1)
            row=np.zeros(nv); row[idx[('u',S,t)]]=1; row[idx[('z',S,t)]]=-1
            A.append(row); lo.append(-np.inf); hi.append(0)
    res=milp(obj,constraints=LinearConstraint(np.array(A),lo,hi),integrality=integ,bounds=Bounds(lb,ub),options={'time_limit':60})
    if res.status != 0 or res.x is None:
        raise RuntimeError(f"MILP did not certify an optimum: {res.message}")
    x={S:{t:res.x[idx[('x',S,t)]] for t in S} for S in msgs}
    return -res.fun, x
if __name__=="__main__":
    for a in (0.6,0.7,0.75,0.8,0.9):
        v,_=solve([a,1-a])
        assert abs(v-a*(1-a))<1e-7, (a,v)
    print("n=2: V* = a(1-a) (MILP, 5 точек).")


# ---- Запас на отношении априоров: геометрические π_j ∝ (1+δ)^(-j), «лестница» -> 1/(1+δ) ----
def ladder_value(pi):
    from fractions import Fraction as Fr
    pi = sorted(pi, reverse=True)
    T = [sum(pi[j:]) for j in range(len(pi))]
    return sum(p * (1 - p / t) for p, t in zip(pi, T))


if __name__ == "__main__":
    from fractions import Fraction as Fr
    for d in (Fr(1), Fr(1, 2), Fr(1, 4)):
        r = 1 + d
        w = [float(r) ** (-j) for j in range(400)]
        pi = [x / sum(w) for x in w]
        assert abs(ladder_value(pi) - float(1 / r)) < 1e-6
    print("Запас δ на отношении априоров: лестница -> 1/(1+δ) (δ=1: 1/2, δ=1/2: 2/3, δ=1/4: 4/5).")
