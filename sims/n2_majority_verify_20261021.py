"""N2: proved block selector, voting amplification, exact LP and budgets.

Standard library, Python >=3.12. Demo responses are synthetic Bernoulli.
"""
from dataclasses import dataclass
from decimal import Decimal as D, getcontext, ROUND_CEILING
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial
from random import Random

getcontext().prec = 70
NODES = (F(0), F(2, 5), F(1))
LAMBDA_BOUND = F(4, 3)


def decimal(x):
    return D(x.numerator) / D(x.denominator)


def ceil(x):
    return int(x.to_integral_value(rounding=ROUND_CEILING))


def f(x):
    return 2*x/(1+x)


def row(x):
    value = f(x)
    return x-value, F(1, 2)-value, F(2, 3)-value


def prediction(x, weights):
    return f(x)+sum(a*b for a, b in zip(row(x), weights))


def solve(rows, rhs):
    a = [list(r)+[b] for r, b in zip(rows, rhs)]
    for j in range(4):
        pivot = next((i for i in range(j, 4) if a[i][j]), None)
        if pivot is None:
            return None
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [v/scale for v in a[j]]
        for i in range(4):
            if i != j:
                scale = a[i][j]
                a[i] = [v-scale*w for v, w in zip(a[i], a[j])]
    return tuple(a[i][-1] for i in range(4))


def fit_catalog(observations):
    constraints = []
    for j in range(4):
        constraints.append((tuple(F(-int(i == j)) for i in range(4)), F(0)))
    constraints.append(((F(1), F(1), F(1), F(0)), F(1)))
    for x, empirical in zip(NODES, observations):
        d, residual = row(x), empirical-f(x)
        constraints.append(((*d, F(-1)), residual))
        constraints.append((tuple(-v for v in d)+(F(-1),), -residual))
    best = None
    for active in combinations(constraints, 4):
        vertex = solve([a for a, _ in active], [b for _, b in active])
        if vertex is None:
            continue
        if all(sum(a*b for a, b in zip(coeff, vertex)) <= limit
               for coeff, limit in constraints):
            if best is None or vertex[3] < best[3]:
                best = vertex
    assert best is not None
    return best[:3]


def binomial_tail(n, p, lo, hi):
    return sum((F(comb(n, j))*p**j*(1-p)**(n-j)
                for j in range(lo, hi+1)), F(0))


@dataclass
class Plan:
    eta: F
    omega: F
    beta: F
    m: int
    k: int
    training: int
    confirmation: int
    stages: list
    flat: int
    mode: str
    block_success: F

    def screening_cost(self):
        if self.mode == 'flat':
            return self.m*self.flat
        return sum(active*n for active, _, n in self.stages)

    def total(self):
        return 3*self.training+self.k*(self.screening_cost()+self.confirmation)


def make_plan(eta=F(1, 5), omega=F(1, 5), beta=F(1, 20), mode='best'):
    assert 0 < eta <= 1 and 0 < omega < 1 and 0 < beta < F(1, 2)
    m = 1
    while F(m)*omega < 2:
        m *= 2
    stages, active, ell = [], m, 1
    while active > 1:
        eps = eta/8*F(3, 4)**(ell-1)
        n = ceil(2/decimal(eps)**2 * D(96*2**ell).ln())
        stages.append((active, eps, n))
        active //= 2
        ell += 1
    assert sum(e for _, e, _ in stages) < eta/2
    assert sum(F(1, 16*2**j) for j in range(1, len(stages)+1)) < F(1, 16)

    # Rational lower bound on hit probability avoids huge exact powers of omega.
    z = m*(omega+omega*omega/2)
    exp_lower = sum((z**j/F(factorial(j)) for j in range(25)), F(0))
    success = (1-1/exp_lower)*F(15, 16)**2
    assert success > F(3, 4)
    k = 1
    while max(binomial_tail(k, F(1, 16), (k+1)//2, k),
              binomial_tail(k, success, 0, (k-1)//2)) > beta/3:
        k += 2
    training = ceil(32*decimal(LAMBDA_BOUND)**2/decimal(eta)**2
                    * (18/decimal(beta)).ln())
    confirmation = ceil(32/decimal(eta)**2*D(32).ln())
    flat = ceil(8/decimal(eta)**2*D(32*m).ln())
    if mode == 'best':
        mode = 'flat' if m*flat <= sum(a*n for a, _, n in stages) else 'halving'
    assert mode in ('flat', 'halving')
    return Plan(eta, omega, beta, m, k, training, confirmation, stages, flat, mode, success)


class BernoulliOracle:
    def __init__(self, probability, seed):
        self.probability, self.rng, self.calls = probability, Random(seed), 0

    def mean(self, x, n):
        self.calls += n
        return F(self.rng.binomialvariate(n, float(self.probability(x))), n)


def select_winner(points, qhat, oracle, plan):
    if plan.mode == 'flat':
        estimates = [abs(oracle.mean(x, plan.flat)-qhat(x)) for x in points]
        return points[max(range(len(points)), key=estimates.__getitem__)]
    for active, _, n in plan.stages:
        assert len(points) == active
        estimates = [abs(oracle.mean(x, n)-qhat(x)) for x in points]
        order = sorted(range(active), key=estimates.__getitem__, reverse=True)
        points = [points[i] for i in order[:active//2]]
    return points[0]


def diagnose(oracle, plan, seed):
    weights = fit_catalog([oracle.mean(x, plan.training) for x in NODES])
    qhat = lambda x: prediction(x, weights)
    rng, votes = Random(seed), 0
    # Demo nu is uniform on this finite grid; theorem permits any sampled nu.
    for _ in range(plan.k):
        points = [F(rng.randrange(1000001), 1000000) for _ in range(plan.m)]
        winner = select_winner(points, qhat, oracle, plan)
        votes += abs(oracle.mean(winner, plan.confirmation)-qhat(winner)) > 3*plan.eta/8
    assert oracle.calls == plan.total()
    return ('UNKNOWN' if 2*votes > plan.k else 'CATALOG'), votes


def balanced_flat_budget(eta, omega, beta, interpolation_bound, ratio=None):
    e, w, b = decimal(eta), decimal(omega), decimal(beta)
    m = ceil((3/b).ln()/-(1-w).ln())
    if ratio is None:
        a = 6*interpolation_bound**2/e**2*(18/b).ln()
        z = 2*m/e**2*(6*m/b).ln()
        ac, zc = (a.ln()/3).exp(), (z.ln()/3).exp()
        ratio = ac/(ac+zc)
    training = ceil(2*interpolation_bound**2/(ratio*e)**2*(18/b).ln())
    validation = ceil(2/((1-ratio)*e)**2*(6*m/b).ln())
    return training, m, validation, ratio


def diagnose_balanced_flat(oracle, eta, omega, beta, seed):
    nt, m, nv, _ = balanced_flat_budget(eta, omega, beta,
                                       decimal(LAMBDA_BOUND), D(3)/8)
    weights = fit_catalog([oracle.mean(x, nt) for x in NODES])
    rng, threshold, rejected = Random(seed), F(11, 16)*eta, False
    for _ in range(m):
        x = F(rng.randrange(1000001), 1000000)
        rejected |= abs(oracle.mean(x, nv)-prediction(x, weights)) > threshold
    assert oracle.calls == 3*nt+m*nv
    return 'UNKNOWN' if rejected else 'CATALOG'


def main():
    for weights in [(F(0), F(1), F(0)), (F(1, 4), F(1, 5), F(1, 10))]:
        inferred = fit_catalog([prediction(x, weights) for x in NODES])
        assert inferred == weights
    print('Exact rational minimax catalogue fit: PASS')
    for omega in (F(1, 5), F(1, 50), F(1, 5000)):
        plan = make_plan(omega=omega)
        pac = make_plan(omega=omega, mode='halving')
        print('BUDGET eta=1/5 beta=1/20 omega=', str(omega),
              'M=', plan.m, 'K=', plan.k, 'train_each=', plan.training,
              'confirm_each=', plan.confirmation, 'screen=', plan.mode,
              'total=', plan.total(), 'pure_halving_total=', pac.total())
        print('  certified block success >=', float(plan.block_success),
              'vote-error bounds=',
              float(binomial_tail(plan.k, F(1, 16), (plan.k+1)//2, plan.k)),
              float(binomial_tail(plan.k, plan.block_success, 0, (plan.k-1)//2)))
    for mode in ('flat', 'halving'):
        plan = make_plan(mode=mode)
        for label, probability in [('NULL', lambda x: F(1, 2)),
                                   ('WIDE_UNKNOWN', lambda x: F(9, 10))]:
            oracle = BernoulliOracle(probability, 20261021)
            decision, votes = diagnose(oracle, plan, 20261022)
            print('SYNTHETIC', mode, label, decision, 'votes=', votes, '/', plan.k,
                  'logical Bernoulli responses=', oracle.calls)
            assert decision == ('CATALOG' if label == 'NULL' else 'UNKNOWN')
    eta, omega, beta = F(1, 5), F(1, 5), F(1, 20)
    root = D(2).sqrt()
    optimal_bound = 1+2*root/((root.sqrt()+1)**2*(root+1))
    for name, bound, ratio in [('optimal nodes / balanced', optimal_bound, None),
                               ('optimal nodes / ratio 3/8', optimal_bound, D(3)/8),
                               ('rational nodes / ratio 3/8', D(4)/3, D(3)/8)]:
        nt, m, nv, a = balanced_flat_budget(eta, omega, beta, bound, ratio)
        print('BALANCED', name, 'a=', float(a), 'train_each=', nt,
              'M=', m, 'validation_each=', nv, 'total=', 3*nt+m*nv)
    for label, probability in [('NULL', lambda x: F(1, 2)),
                               ('WIDE_UNKNOWN', lambda x: F(9, 10))]:
        oracle = BernoulliOracle(probability, 20261021)
        decision = diagnose_balanced_flat(oracle, eta, omega, beta, 20261022)
        print('SYNTHETIC balanced', label, decision, 'logical responses=', oracle.calls)
        assert decision == ('CATALOG' if label == 'NULL' else 'UNKNOWN')
    print('PASS; synthetic runs check execution, not the uniform error theorem')


if __name__ == '__main__':
    main()
