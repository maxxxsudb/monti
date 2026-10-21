"""Global chest optima and certified integer optimum of a fixed N2 design."""
from decimal import Decimal as D, getcontext, ROUND_CEILING
from fractions import Fraction as F
import json
from pathlib import Path

from focus_followup_verify_20261021 import chests
from next_tasks_independent_audit_20261021 import Interval
from n2_majority_verify_20261021 import BernoulliOracle, fit_catalog, prediction, NODES
from random import Random

getcontext().prec = 75


def log_interval(value):
    value = F(value)
    assert value >= 1
    power = 0
    while value >= 2:
        value /= 2
        power += 1

    def series(x):
        z, terms = (x-1)/(x+1), 60
        lower = 2*sum((z**(2*j+1)/F(2*j+1) for j in range(terms)), F(0))
        tail = 2*z**(2*terms+1)/(F(2*terms+1)*(1-z*z))
        return Interval(lower, lower+tail)

    return power*series(F(2))+series(value)


def decimal(value):
    return D(value.numerator)/D(value.denominator)


def ceil_fraction(value):
    return -(-value.numerator//value.denominator)


def feasible(c, z, nt, nv):
    x, y = c/nt, z/nv
    rest = 1-x-y
    return rest >= 0 and rest*rest >= 4*x*y


def integer_certificate(label, norm):
    eta, beta, m = F(1, 5), F(1, 20), 17
    assert F(4, 5)**m <= beta/2 < F(4, 5)**(m-1)
    c = 2/(eta*eta)*norm*norm*log_interval(12/beta)
    z = 2/(eta*eta)*log_interval(4*m/beta)
    nt0, nv0 = ceil_fraction(c.hi/F(3, 8)**2), ceil_fraction(z.hi/F(5, 8)**2)
    upper = 3*nt0+m*nv0
    best = (upper, nt0, nv0)
    checked = 0
    for nt in range(c.lo.numerator//c.lo.denominator+1, (upper-m)//3+1):
        assert c.hi < nt
        nv = int((decimal(z.hi)/(1-(decimal(c.hi)/nt).sqrt())**2)
                 .to_integral_value(rounding=ROUND_CEILING))
        while not feasible(c.hi, z.hi, nt, nv):
            nv += 1
        while nv > 1 and feasible(c.hi, z.hi, nt, nv-1):
            nv -= 1
        assert not feasible(c.lo, z.lo, nt, nv-1)
        checked += 1
        best = min(best, (3*nt+m*nv, nt, nv))
    total, nt, nv = best
    lo = (Interval(c.lo/nt, c.hi/nt).sqrt()).hi
    hi = 1-(Interval(z.lo/nv, z.hi/nv).sqrt()).hi
    assert lo < hi
    scale = 10**8
    a = F(ceil_fraction(lo*scale), scale)
    assert lo <= a <= hi
    assert c.hi <= nt*a*a and z.hi <= nv*(1-a)**2
    print('N2 CERTIFIED', label, 'total=', total, 'train_each=', nt,
          'M=', m, 'validation_each=', nv, 'a=', str(a), 'checked_nt=', checked)
    return {'label': label, 'total': total, 'training': nt, 'm': m, 'validation': nv,
            'a': str(a), 'checked_nt': checked, 'C': [str(c.lo), str(c.hi)],
            'Z': [str(z.lo), str(z.hi)],
            'scope': 'fixed M=17, equal training counts, equal validation counts, '
                     'beta/2 per relevant failure term, Hoeffding/projection certificate'}


def chest_optima():
    best, weighted = (F(0), None), (F(0), None)
    checked = 0
    for n in range(3, 15):
        for a in range(2, n):
            for b in range(1, a):
                if a+b <= n:
                    continue
                pi, own, other = chests(n, a, b)
                gap = own-other
                event = F(a*(n-a)+b*(n-b), 2*n*(n-1))
                if gap == F(2, 25):
                    assert (n, a, b) == (5, 4, 3)
                if event*gap == F(1, 48):
                    assert (n, a, b) == (4, 3, 2)
                if n <= 11 and gap > best[0]:
                    best = gap, (n, a, b)
                if event*gap > weighted[0]:
                    weighted = event*gap, (n, a, b)
                checked += 1
    assert best == (F(2, 25), (5, 4, 3))
    assert weighted == (F(1, 48), (4, 3, 2))
    assert F(9, 12*10) < F(2, 25)
    assert F(15, 4*14*13) < F(1, 48)
    print('CHESTS GLOBAL conditional optimum=', best, '; original-trial optimum=', weighted)
    print('  Finite enumeration below analytic cutoffs; beyond cutoffs monotone upper bounds prove exclusion')
    for n in range(3, 20):
        for a in range(2, n):
            for b in range(1, a):
                for r in range(b+1):
                    for s in range(n-a+1):
                        m = r+s
                        if not 0 < m < n:
                            continue
                        d = a-b
                        threshold = F(n*d-m*a+n*r, (2*n-m)*d)
                        assert threshold-F(1, 2) == F(2*n*r-m*(a+b), 2*(2*n-m)*d)
                        for pi in (F(1, 4), F(1, 2), F(3, 4)):
                            own = (b+pi*d-r)/(n-m)
                            other = (a-pi*d)/n
                            assert own-other == F((2*n-m)*d, n*(n-m))*(pi-threshold)
    print('GENERAL focus threshold for arbitrary supported removed colours PASS')


def synthetic_certificate(config):
    eta, beta, a = F(1, 5), F(1, 20), F(config['a'])
    nt, m, nv = config['training'], config['m'], config['validation']
    for label, probability in [('NULL', lambda x: F(1, 2)),
                               ('UNKNOWN', lambda x: F(9, 10))]:
        oracle, rng = BernoulliOracle(probability, 20261021), Random(20261022)
        weights = fit_catalog([oracle.mean(x, nt) for x in NODES])
        reject = False
        for _ in range(m):
            x = F(rng.randrange(1000001), 1000000)
            reject |= abs(oracle.mean(x, nv)-prediction(x, weights)) > (1+a)*eta/2
        assert reject == (label == 'UNKNOWN')
        assert oracle.calls == config['total']
        print('SYNTHETIC certified rational design', label, 'reject=', reject, 'logical answers=', oracle.calls)


def main():
    root = Interval.point(2).sqrt()
    q = root.sqrt()+1
    optimal = 1+2*root/(q*q*(root+1))
    rational = 18-2*Interval.point(70).sqrt()
    left = 17-F(8, 3)*Interval.point(35).sqrt()
    assert left.hi < rational.lo
    results = [integer_certificate('optimal nodes', optimal),
               integer_certificate('rational nodes, exact norm', rational),
               integer_certificate('rational nodes, bound 4/3', Interval.point(F(4, 3)))]
    assert [c['total'] for c in results] == [24751, 25082, 26074]
    chest_optima()
    synthetic_certificate(results[1])
    output = Path(__file__).resolve().parents[1]/'research/counterintuition-final/n2-integer-certificate-2026-10-21.json'
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('PASS; exact within the stated finite design, not a universal finite minimax claim')


if __name__ == '__main__':
    main()
