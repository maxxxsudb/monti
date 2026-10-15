# r0c_experts: '90+80 independent beats 90+90 correlated'? Exact optimum over ALL 16 rules for 2 binary voters; 3-voter case.
import random, itertools
random.seed(3); T = 10**6
def joint_indep(p1, p2):  # P(v1 correct, v2 correct)
    return {(a, b): (p1 if a else 1-p1)*(p2 if b else 1-p2) for a in (0,1) for b in (0,1)}
def joint_corr(p, rho):   # two Bern(p) correctness indicators with correlation rho
    both = p*p + rho*p*(1-p)
    return {(1,1): both, (1,0): p-both, (0,1): p-both, (0,0): 1-2*p+both}
def best_rule(J):
    # truth Y uniform in {0,1}; vote_i = Y if correct else 1-Y. Rule: f(v1,v2)->{0,1}. 16 rules.
    best = 0
    for f in itertools.product((0,1), repeat=4):
        acc = 0
        for Yv in (0,1):
            for (a,b), pr in J.items():
                v1 = Yv if a else 1-Yv; v2 = Yv if b else 1-Yv
                acc += 0.5*pr*(f[2*v1+v2] == Yv)
        best = max(best, acc)
    return best
for name, J in [("90+90 rho=0.9", joint_corr(.9,.9)), ("90+90 rho=0", joint_corr(.9,0)), ("90+80 indep", joint_indep(.9,.8)), ("90+90 rho=1", joint_corr(.9,1))]:
    print(f"{name:14s}: best accuracy over all 16 rules = {best_rule(J):.4f}")
# MC: 90+80 independent, rule 'follow 90 when disagree'
ok = 0
for _ in range(T):
    a = random.random() < .9; b = random.random() < .8
    ok += a  # agree->both right iff a; disagree->follow expert1
print(f"MC 90+80 indep, follow best: {ok/T:.4f} (=0.90, cannot exceed best member)")
# 3 voters majority: {90,90 (rho high), 80} vs {90,90,90 all rho high}? compare {A,A',C}: A,A' corr rho, C indep
def maj3(pa, rho, pc, n=T):
    both = pa*pa + rho*pa*(1-pa); ok = 0
    for _ in range(n):
        u = random.random()
        a, b = (1,1) if u < both else (1,0) if u < pa else (0,1) if u < 2*pa-both else (0,0)
        c = random.random() < pc
        ok += (a+b+c) >= 2
    exact = both + (pa-both)*2*pc
    return ok/n, exact
for pc, lbl in ((.9, "third=90 corr? no: indep 90"), (.8, "third=80 indep")):
    mc, ex = maj3(.9, .9, pc)
    print(f"majority of [90,90 rho=.9] + {lbl}: MC={mc:.4f} exact={ex:.4f}")
# trio of three 90% all pairwise rho=.9 ~ near 0.90; compare with two corr 90 + indep 80
mc, ex = maj3(.9, 1.0, .8); print(f"majority [90,90 identical] + 80 indep: {ex:.4f} (=0.90)")
print(f"3 independent 90s: exact {0.9**3+3*0.9**2*0.1:.4f}; [90,80,80] indep: {0.9*0.8*0.8+0.9*2*0.8*0.2+0.1*0.64:.4f}")
# Asymmetric (class-conditional) errors: A sens=1 spec=.8 (acc .9); C sens=1 spec=.6 (acc .8) indep; A+clone = .9
def best_rule_cc(pairs):  # pairs[Y] = dict {(v1,v2): prob}
    best = 0
    for f in itertools.product((0,1), repeat=4):
        acc = sum(0.5*pr*(f[2*v1+v2] == Yv) for Yv in (0,1) for (v1,v2), pr in pairs[Yv].items())
        best = max(best, acc)
    return best
def indep_cc(sA, pA, sC, pC):  # sens s = P(vote1|Y=1), spec p = P(vote0|Y=0)
    d = {}
    for Yv in (0,1):
        a1 = sA if Yv else 1-pA; c1 = sC if Yv else 1-pC
        d[Yv] = {(v1,v2): (a1 if v1 else 1-a1)*(c1 if v2 else 1-c1) for v1 in (0,1) for v2 in (0,1)}
    return d
clone = {1: {(1,1): 1.0}, 0: {(1,1): .2, (0,0): .8}}
print(f"asym: A(sens1,spec.8)+clone best={best_rule_cc(clone):.4f}; A+C(sens1,spec.6) indep best={best_rule_cc(indep_cc(1,.8,1,.6)):.4f} (exact 0.96)")
ok = 0
for _ in range(T):
    Yv = random.random() < .5
    a = 1 if Yv else (random.random() < .2); c = 1 if Yv else (random.random() < .4)
    pred = 1 if (a and c) else 0
    ok += pred == Yv
print(f"MC asym A+C rule 'AND': {ok/T:.4f}")
# MC for 3-member: [90,90,90 clones]=.90 vs [90,80,80] indep
ok1 = ok2 = 0
for _ in range(T):
    a = random.random() < .9; ok1 += a
    ok2 += (a + (random.random() < .8) + (random.random() < .8)) >= 2
print(f"MC 3 clones of 90: {ok1/T:.4f} (exact .900); [90,80,80] indep majority: {ok2/T:.4f} (exact .928)")
