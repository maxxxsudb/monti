"""Exact checks for candidates from two new source texts (2026-10-28).

Sources: research/inputs/2026-10-28-argon-chatgpt/ (argon.txt, chatgpt-paradox-2.txt).
Only fractions.Fraction. Where possible two methods: physical enumeration of
outcomes and a closed formula. Every printed claim is also an assert.

Section map (same numbering as the report NEW-VIEW-2026-10-28.md):
 1  Inverse Monty (candidate "Sapper" from argon.txt; here neutral words:
    one BAD door, two GOOD doors, host opens a GOOD door)
 2  Two auditors (k agreeing auditors), payout ratio r, robustness in h
 3  Certificate paradox (selection into test) + improving the screen
 4  Useless first test: one-step VOI = 0, full sequential DP
 5  Exactly one vs at least one alarm
 6  Three YES vs one NO (independent vs copies)
 7  Two individually useless indicators
 8  Four-cell 3+3: compression loss and the tie of the compressed solver
 9  Lemma: for two actions Delta_trap = Regret/2
10  Strategy-signature battery: identifiability by rank
"""
from fractions import Fraction as F
from itertools import product
import math

LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LINES.append(s)


def head(t):
    say('')
    say('=' * 72)
    say(t)
    say('=' * 72)


# ---------------------------------------------------------------- 1
def inverse_physical(a, b, h, opened=2):
    """P(bad behind door | host opened `opened`). Player holds door 1.
    Priors of BAD: door1=a, door2=b, door3=b. Host opens a GOOD door among
    {2,3}; if both good, opens 2 with prob h."""
    pri = {1: a, 2: b, 3: b}
    joint = {}
    for bad in (1, 2, 3):
        good = [d for d in (2, 3) if d != bad]
        ch = {2: h, 3: 1 - h} if len(good) == 2 else {good[0]: F(1)}
        for d, m in ch.items():
            joint[(bad, d)] = joint.get((bad, d), F(0)) + pri[bad] * m
    ev = sum(m for (bb, d), m in joint.items() if d == opened)
    return {x: sum(m for (bb, d), m in joint.items() if d == opened and bb == x) / ev
            for x in (1, 2, 3)}


def inverse_formula(a, b, h):
    p1 = a * h / (a * h + b)
    return p1, 1 - p1          # P(bad at 1), P(bad at 3) | door 2 opened


def sec1():
    head('1. Inverse Monty (argon.txt "Sapper"): host opens a GOOD door')
    for name, a, b in (('symmetric 1/3', F(1, 3), F(1, 3)),
                       ('40/30/30', F(2, 5), F(3, 10))):
        h = F(1, 2)
        post = inverse_physical(a, b, h)
        p1, p3 = inverse_formula(a, b, h)
        assert post[1] == p1 and post[3] == p3 and post[2] == 0
        stay, switch = 1 - p1, 1 - p3          # P(good) of action
        n1, n3 = a / (a + b), b / (a + b)      # protocol-blind posterior
        say(f'{name}: true P(good) stay={stay} switch={switch};'
            f' protocol-blind P(good) stay={1-n1} switch={1-n3}')
        best = 'stay' if stay > switch else 'switch'
        naive = 'stay' if 1 - n1 > 1 - n3 else 'switch' if 1 - n1 < 1 - n3 else 'tie'
        say(f'   best={best}; protocol-blind={naive}; rule "always switch"=switch;'
            f' default=stay; regret(switch)={stay-switch}; Delta_trap={(stay-switch)/2}')
        assert best == 'stay'
    # trap region with h=1/2: naive switch iff a>b, true stay iff b>a/2
    say('Trap region (h=1/2, a+2b=1): protocol-blind says switch AND truth says stay'
        ' <=> b<a<2b <=> 1/3<a<1/2')
    for k in range(1, 60):
        a = F(k, 60)
        b = (1 - a) / 2
        if b <= 0:
            continue
        p1, p3 = inverse_formula(a, b, F(1, 2))
        trap = (a > b) and (p3 > p1)
        assert trap == (F(1, 3) < a < F(1, 2)), a
    # robustness to host tie-break h
    for name, a, b in (('symmetric', F(1, 3), F(1, 3)), ('40/30/30', F(2, 5), F(3, 10))):
        thr = b / a
        for j in range(0, 101):
            h = F(j, 100)
            p1, p3 = inverse_formula(a, b, h)
            assert (p3 > p1) == (h < thr)
        say(f'robustness {name}: stay is strictly better iff h < {thr}'
            f' (h = prob. host opens door 2 when both are good)')
    say('Structural Monty knower maps BAD<->car: the special object concentrates on the'
        ' other closed door (2/3) -> stay. Surface rule "switch" loses 1/3.')


# ---------------------------------------------------------------- 2
def auditors_physical(k, h):
    mass = {}
    for prize in 'ABC':
        empties = [d for d in 'BC' if d != prize]
        for names in product('BC', repeat=k):
            m = F(1, 3)
            for nm in names:
                if len(empties) == 2:
                    m *= h if nm == 'B' else 1 - h
                else:
                    m *= 1 if nm == empties[0] else 0
            if m:
                mass[(prize, names)] = mass.get((prize, names), F(0)) + m
    allb = tuple('B' * k)
    ev = sum(m for (p, n), m in mass.items() if n == allb)
    pa = sum(m for (p, n), m in mass.items() if n == allb and p == 'A') / ev
    pc = sum(m for (p, n), m in mass.items() if n == allb and p == 'C') / ev
    pdis = sum(m for (p, n), m in mass.items() if len(set(n)) > 1)
    return pa, pc, pdis


def sec2():
    head('2. Two auditors: k independent auditors all name empty door B')
    for k in (1, 2, 3):
        pa, pc, pdis = auditors_physical(k, F(1, 2))
        assert pa == F(1, 2 ** k + 1) and pc == 1 - pa
        say(f'k={k}: P(prize own A)={pa}, P(prize C)={pc}; P(auditors disagree)={pdis}'
            f'  (= biased-host Monty with q=2^-k, Morgan et al. 1991)')
    say('Disagreement is possible only if prize is behind A -> agreement is evidence for C.')
    for r in (F(5, 2), F(3)):
        for k in (1, 2, 3):
            pa, pc, _ = auditors_physical(k, F(1, 2))
            st, sw = r * pa, pc
            say(f'payout ratio r={r} (stay pays r, switch pays 1), k={k}: EV stay={st},'
                f' switch={sw} -> {"stay" if st > sw else "switch"}')
        say(f'   Monty-copy solver (1/3 vs 2/3) at r={r}: stay={r/3} switch={F(2,3)} ->'
            f' {"stay" if r/3 > F(2,3) else "switch"}; protocol-blind (1/2,1/2): stay')
    say('Decision flips exactly at k with 2^(k-1) < r < 2^k (h=1/2). r in (2,4): one auditor ->'
        ' stay, two -> switch.')
    say('Robustness to auditor tie-break h: k=1 stay iff h>1/r; k=2 switch iff h<1/sqrt(r).')
    for r in (F(5, 2), F(3)):
        lo, hi = 1 / r, 1 / math.sqrt(r)
        say(f'   r={r}: valid h in ({float(lo):.4f}, {hi:.4f}); min distance from 1/2 ='
            f' {min(0.5-float(lo), hi-0.5):.4f}')
    phi2 = ((1 + 5 ** 0.5) / 2) ** 2
    say(f'   max-min robust ratio solves 1/r+1/sqrt(r)=1 -> r=phi^2={phi2:.4f};'
        f' margin {0.5-1/phi2:.4f}. r=5/2 is the nearest simple choice.')
    # check equation
    assert abs(1 / phi2 + 1 / math.sqrt(phi2) - 1) < 1e-12


# ---------------------------------------------------------------- 3
def cert(p, sB, sG, tB, tG):
    bc, gc = p * sB * tB, (1 - p) * sG * tG
    bu, gu = p * (1 - sB), (1 - p) * (1 - sG)
    c = bc / (bc + gc)
    u = bu / (bu + gu)
    sold = (bc + bu) / (bc + gc + bu + gu)
    return c, u, sold


def sec3():
    head('3. Certificate paradox: selection into the test')
    # physical count 1000 units
    bad, good = 200, 800
    sent_b, sent_g = 160, 80
    pass_b, pass_g = 40, 60
    c_phys = F(pass_b, pass_b + pass_g)
    u_phys = F(bad - sent_b, bad - sent_b + good - sent_g)
    sold_phys = F(pass_b + bad - sent_b, pass_b + pass_g + bad - sent_b + good - sent_g)
    c, u, sold = cert(F(1, 5), F(4, 5), F(1, 10), F(1, 4), F(3, 4))
    assert (c, u, sold) == (c_phys, u_phys, sold_phys)
    say(f'base: P(bad|certified)={c}, P(bad|untested)={u}, P(bad|sold)={sold}'
        f' = {float(sold):.4f}; ratio {float(c/u):.2f}x')
    c2, u2, s2 = cert(F(1, 5), F(1), F(1, 10), F(1, 4), F(3, 4))
    say(f'screen improved sB 4/5->1: certified={c2}={float(c2):.4f}, sold={s2}={float(s2):.4f}')
    assert c2 > c and s2 < sold
    say('Theorem A: certified worse than untested <=> DOR(screen)=sB(1-sG)/(sG(1-sB)) > tG/tB.')
    say('Theorem B: odds(bad|certified) ~ sB; bad sold ~ p[(1-sB)+sB tB] decreasing if tB<1.')
    grid = [F(i, 10) for i in range(1, 10)]
    n = 0
    for sB, sG, tB, tG in product(grid, grid, grid, grid):
        if tB >= tG:
            continue      # informative test only
        c, u, _ = cert(F(1, 5), sB, sG, tB, tG)
        assert (c > u) == (sB * (1 - sG) / (sG * (1 - sB)) > tG / tB)
        n += 1
    for sG, tB, tG in product(grid, grid, grid):
        prev = None
        for sB in grid:
            c, u, s = cert(F(1, 5), sB, sG, tB, tG)
            if prev:
                assert c > prev[0] and s < prev[1]
            prev = (c, s)
    say(f'Theorem A checked on {n} grid points; Theorem B monotonicity on full 9^4 grid.')
    say(f'decision "buy certified vs untested": P(good) {1-F(2,5)} vs {1-F(1,19)};'
        f' regret {F(18,19)-F(3,5)}')


# ---------------------------------------------------------------- 4
def first_test_dp(p0=F(1, 5), acc=F(3, 4), reward=100, cost=2, horizon=40):
    lr = acc / (1 - acc)
    o0 = p0 / (1 - p0)

    def pb(n):
        o = o0 * lr ** n
        return o / (1 + o)

    def stop(n):
        x = pb(n)
        return reward * max(x, 1 - x)

    V = {n: stop(n) for n in range(-horizon - 1, horizon + 2)}
    values = {0: V[0]}
    policy = None
    for left in range(1, horizon + 1):
        NV, pol = {}, {}
        for n in range(-horizon, horizon + 1):
            x = pb(n)
            pplus = x * acc + (1 - x) * (1 - acc)
            cont = -cost + pplus * V[n + 1] + (1 - pplus) * V[n - 1]
            NV[n] = max(stop(n), cont)
            pol[n] = cont > stop(n)
        V = {**V, **NV}
        values[left] = V[0]
        policy = pol
    return values, policy, pb


def sec4():
    head('4. Useless first test: myopic VOI zero, sequential VOI positive')
    pb = lambda n: F(1, 4) * 3 ** n / (1 + F(1, 4) * 3 ** n)
    assert pb(1) == F(3, 7) and pb(-1) == F(1, 13) and pb(2) == F(9, 13)
    say(f'P(bad)=1/5; after +: {pb(1)}, after -: {pb(-1)} -> accept in both: one-step VOI=0')
    values, policy, _ = first_test_dp()
    for L in (0, 1, 2, 3, 4, 6, 10, 40):
        say(f'max {L:>2} tests allowed: optimal expected score = {float(values[L]):.4f}'
            f'  (gain over no test {float(values[L]-80):+.4f})')
    assert values[1] == 80 and values[2] == F(8355, 100)
    cont = sorted(n for n, v in policy.items() if v)
    say(f'unlimited tests (horizon 40): continue testing at net count n in {cont}; stop otherwise')
    say('  n = (#positive - #negative); posterior odds of bad = (1/4)*3^n')
    say('Correction to chatgpt-paradox-2: "test, then second only after +" (=83.55) is optimal'
        ' only under max 2 tests. Without the cap the optimal policy keeps testing at n=2'
        ' (P(bad)=9/13) and the value is higher.')
    # family boundary
    for k in range(1, 100):
        p = F(k, 100)
        o = p / (1 - p)
        one_flat = 3 * o < 1                 # after + still accept
        two_flip = 9 * o > 1                 # after ++ reject
        assert (one_flat and two_flip) == (F(1, 10) < p < F(1, 4))
    say('family: one test never flips & two positives flip <=> 1/10 < p < 1/4 (checked).')


# ---------------------------------------------------------------- 5
def alarm_physical(n, p, exactly):
    tot = F(0)
    for pat in product((0, 1), repeat=n):
        m = F(1)
        for x in pat:
            m *= p if x else 1 - p
        s = sum(pat)
        if (s == 1) if exactly else (s >= 1):
            tot += m
    return tot


def sec5():
    head('5. Exactly one vs at least one alarm (types: 1 fault vs 4 faults, p=3/4)')
    p = F(3, 4)
    e1, e4 = alarm_physical(1, p, True), alarm_physical(4, p, True)
    assert e4 == 4 * p * (1 - p) ** 3 == F(3, 64)
    post1 = e1 / (e1 + e4)
    a1, a4 = alarm_physical(1, p, False), alarm_physical(4, p, False)
    post4 = a4 / (a1 + a4)
    assert post1 == F(16, 17) and post4 == F(85, 149)
    say(f'"exactly one": P(1 fault)={post1}; "at least one": P(4 faults)={post4}')
    for n in (2, 3, 4, 6):
        thr = 1 - n ** (-1 / (n - 1))
        for j in range(1, 200):
            q = F(j, 200)
            if abs(float(q) - thr) < 1e-9:
                continue
            assert (n * (1 - q) ** (n - 1) < 1) == (float(q) > thr)
        say(f'n={n}: "exactly one" favours 1 fault iff p > 1-n^(-1/(n-1)) = {thr:.4f}')


# ---------------------------------------------------------------- 6, 7
def sec6_7():
    head('6. Three YES (75%) vs one NO (80%)')
    ind = F(3) ** 3 / 4
    cop = F(3) / 4
    say(f'independent: odds {ind} -> P(true)={ind/(1+ind)}; copies: odds {cop} -> {cop/(1+cop)}')
    assert ind / (1 + ind) == F(27, 31) and cop / (1 + cop) == F(3, 7)
    head('7. Two individually useless indicators')
    joint = {}
    for state, pg, pm in (('good', F(2, 5), F(9, 10)), ('bad', F(3, 5), F(1, 10))):
        for c1, c2 in product('RB', repeat=2):
            m = pm / 2 if c1 == c2 else (1 - pm) / 2
            joint[(state, c1, c2)] = pg * m
    for state, pg in (('good', F(2, 5)), ('bad', F(3, 5))):
        assert sum(v for (s, c1, c2), v in joint.items() if s == state and c1 == 'R') == pg / 2
    same = sum(v for (s, a, b), v in joint.items() if a == b)
    pg_same = sum(v for (s, a, b), v in joint.items() if a == b and s == 'good') / same
    diff = 1 - same
    pg_diff = sum(v for (s, a, b), v in joint.items() if a != b and s == 'good') / diff
    assert pg_same == F(6, 7) and pg_diff == F(2, 29)
    say(f'each colour alone: P(red|state)=1/2 for both states; match -> P(good)={pg_same};'
        f' mismatch -> {pg_diff}')


# ---------------------------------------------------------------- 8
def sec8():
    head('8. Four-cell 3+3: compression loss and tie of compressed solver')
    cells = {('S', 'rem'): (F(2, 3), F(5, 9)), ('S', 'ret'): (F(4, 9), F(5, 9)),
             ('G', 'rem'): (F(1, 3), F(4, 9)), ('G', 'ret'): (F(5, 9), F(4, 9))}
    vfull = sum(max(v) for v in cells.values()) / 4
    vg = F(0)
    for col in 'SG':
        own = (cells[(col, 'rem')][0] + cells[(col, 'ret')][0]) / 2
        oth = (cells[(col, 'rem')][1] + cells[(col, 'ret')][1]) / 2
        say(f'colour {col} without "returned": own={own} other={oth} -> margin {own-oth}')
        assert own == oth
        vg += max(own, oth) / 2
    assert vfull == F(5, 9) and vg == F(1, 2)
    say(f'V_full={vfull}, V_g={vg}, L_g={vfull-vg}. Best compressed solver is exactly indifferent:'
        ' direction must come from a reconstruction prior -> HEURISTIC_UNKNOWN for 3+3.')
    say('S-removed cell: correct=own=default (keep own bag). Refusal + keep -> correct answer.')


# ---------------------------------------------------------------- 9
def sec9():
    head('9. Lemma: two actions => Delta_trap = Regret/2 (criterion 3 of argon is automatic)')
    examples = {'classic Monty': (F(2, 3), F(1, 3)), '3+3 S-removed': (F(2, 3), F(5, 9)),
                'inverse Monty sym': (F(2, 3), F(1, 3)), 'auditors k=2 r=5/2': (F(4, 5), F(1, 2))}
    for k, (qs, qw) in examples.items():
        rnd = (qs + qw) / 2
        assert rnd - qw == (qs - qw) / 2
        say(f'{k}: Q*={qs}, Q(shortcut)={qw}, Q(random)={rnd}, Delta_trap={rnd-qw}=R/2')
    say('Informative baseline is the DEFAULT action d (what refusal produces), not uniform random.')


# ---------------------------------------------------------------- 10
def rank(rows):
    m = [list(r) for r in rows]
    rk, col, ncol = 0, 0, len(m[0])
    while rk < len(m) and col < ncol:
        piv = next((i for i in range(rk, len(m)) if m[i][col] != 0), None)
        if piv is None:
            col += 1
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][col] != 0:
                f = m[i][col] / m[rk][col]
                m[i] = [x - f * y for x, y in zip(m[i], m[rk])]
        rk += 1
        col += 1
    return rk


def pattern_vectors(types, nitems):
    pats = list(product((0, 1), repeat=nitems))
    vecs = {}
    for name, sig in types.items():
        if sig is None:
            vecs[name] = [F(1, 2 ** nitems)] * len(pats)
        else:
            vecs[name] = [F(int(p == sig)) for p in pats]
    return vecs


def sec10():
    head('10. Strategy-signature battery (1=switch, 0=stay)')
    items = ['classic Monty', 'inverse sym', 'inverse 40/30/30', 'auditors k=2 r=5/2']
    correct = (1, 0, 0, 1)
    types4 = {'N full model': (1, 0, 0, 1), 'R rule always-switch': (1, 1, 1, 1),
              'M Monty-copy 1/3:2/3': (1, 0, 0, 0), 'P protocol-blind': (0, 0, 1, 0),
              'I inertia/default': (0, 0, 0, 0), 'U random': None}
    say('items: ' + ' | '.join(items) + f'; correct={correct}')
    for k, v in types4.items():
        if v:
            say(f'  {k:<24} {v}  errors={sum(a != b for a, b in zip(v, correct))}')
    sigs = [v for v in types4.values() if v]
    assert len(set(sigs)) == len(sigs)
    vec = pattern_vectors(types4, 4)
    rk = rank(list(vec.values()))
    say(f'joint-pattern vectors (16 patterns, 6 types incl. random): rank {rk} -> mixture identifiable')
    assert rk == 6
    types2 = {'S structural': (1, 0), 'R rule': (1, 1), 'I inertia': (0, 0), 'U random': None}
    rk2 = rank(list(pattern_vectors(types2, 2).values()))
    assert rk2 == 4
    say('two-item core (classic, inverse sym): P(sw,sw)=R+U/4, P(sw,st)=S+U/4,'
        ' P(st,sw)=U/4, P(st,st)=I+U/4 -> rank 4, closed-form inversion.')
    say('Protocol-blind P coincides with inertia on the two-item core (ties -> default);'
        ' the 40/30/30 item separates them, the auditors item separates N from M.')


def main():
    sec1(); sec2(); sec3(); sec4(); sec5(); sec6_7(); sec8(); sec9(); sec10()
    say('')
    say('ALL ASSERTIONS PASSED')


if __name__ == '__main__':
    main()
