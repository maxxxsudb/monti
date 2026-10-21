"""Exact independent checks of the two submitted all-task packages."""
from fractions import Fraction as F
from itertools import combinations, permutations
from math import comb

from next_tasks_independent_audit_20261021 import lagrange_rows


def multiply(p, q):
    result = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            result[i + j] += a * b
    return result


def determinant(rows):
    return sum(rows[0][j]
               * (rows[1][(j + 1) % 3] * rows[2][(j + 2) % 3]
                  - rows[1][(j + 2) % 3] * rows[2][(j + 1) % 3])
               for j in range(3))


def check_design():
    count = 0
    for nodes in combinations([F(i, 10) for i in range(11)], 3):
        a, b, c = nodes
        rp, re, rc = [sum(abs(v) for v in row) for row in lagrange_rows(nodes)]
        assert re == 6 + 2 * (2*a*c - a - c + 1) * rp
        assert rc == 6 + F(3, 2) * (3*a*c - a - c + 1) * rp
        rows = []
        for x in nodes:
            f = 2*x/(1+x)
            rows.append([x-f, F(1, 2)-f, F(2, 3)-f])
        assert determinant(rows) == (b-a)*(c-a)*(c-b)/(3*(1+a)*(1+b)*(1+c))
        count += 1
    print('N1 row norms and POSITIVE determinant:', count, 'rational triples PASS')

    for s, t in [(F(1), F(6, 5)), (F(1), F(4, 3)),
                 (F(11, 10), F(7, 5)), (F(6, 5), F(7, 5))]:
        a, b, c = s*s-1, s*t-1, t*t-1
        coefficients = [F(1), F(2), F(1), F(0), F(0)]
        k = F(0)
        for i, x in enumerate((a, b, c)):
            y, z = [v for j, v in enumerate((a, b, c)) if j != i]
            w = (1+x)/((x-y)*(x-z))
            numerator = [w*y*z, -w*(y+z), w]
            for j, value in enumerate(multiply(numerator, numerator)):
                coefficients[j] -= value
            k += w*w
        assert k == 2*(s*s+s*t+t*t)/((t-s)**4*(t+s)**2)
        factored = multiply(multiply([-a, F(1)], [c, F(-1)]),
                            multiply([-b, F(1)], [-b, F(1)]))
        assert coefficients == [k*v for v in factored]
    print('N1 squared-weight identity: exact POLYNOMIAL coefficients PASS')


def check_claims():
    for ell, n in [(5, 298), (6, 314)]:
        lower, upper = (3*n+7)//8, 5*n//8
        actual = sum(F(comb(n, k)*7**k*3**(n-k), 10**n)
                     for k in range(lower, upper+1))
        assert actual > F(1, 16*ell*ell)
        print('N2 exact absolute-residual failure:', ell, n, float(actual), 'REFUTES claimed bound')

    count = 0
    for i in range(1, 21):
        for j in range(i):
            g, e = F(i, 20), F(j, 20)
            for structural in (False, True):
                x = g*e if structural else e*e
                profiles = [(1, 1, 1), (g, e, g), (e, g, g), (e, e, e), (x, x, g*g)]
                actual = min(max(abs(a-b) for a, b in zip(p, q))
                             for p, q in combinations(profiles, 2))
                expected = min(g-e, max(e*(1-g if structural else 1-e), abs(g*g-e)))
                assert actual == expected
                count += 1
    print('R1 repaired formulas:', count, 'exact parameter/table cases PASS')


def check_attack():
    omega, eta = F(1, 200), F(1, 4)
    width = 6*omega
    supports = []
    for left, right in [(F(2, 100), F(38, 100)), (F(42, 100), F(98, 100))]:
        for i in range((right-left)//width):
            supports.append((left+i*width, left+(i+1)*width))
    assert len(supports) >= 1/(10*omega)

    def p(x, left):
        for i in range(8):
            start = left + i*F(3, 4)*omega
            ramp_end, plateau_end = start+omega/8, start+5*omega/8
            end = start+3*omega/4
            sign = 1 if i % 2 == 0 else -1
            if start <= x <= end:
                if x < ramp_end:
                    return F(1, 2)+sign*eta*(x-start)/(omega/8)
                if x <= plateau_end:
                    return F(1, 2)+sign*eta
                return F(1, 2)+sign*eta*(end-x)/(omega/8)
        return F(1, 2)

    for left, right in supports:
        assert right-left == width
        for x in (F(0), F(2, 5), F(1)):
            assert p(x, left) == F(1, 2)
        for i in range(8):
            center = left+i*F(3, 4)*omega+F(3, 8)*omega
            assert p(center, left) == F(1, 2)+(eta if i % 2 == 0 else -eta)
        for i in range(9):
            assert p(left+i*F(3, 4)*omega, left) == F(1, 2)
    print('N2 corrected CONTINUOUS disjoint four-pair family:', len(supports), 'supports PASS')
    print('  Universal separation uses the quadratic root-count proof, not a catalogue grid')


def check_paradoxes():
    for reserve in (False, True):
        rates = []
        for gold in (3, 2):
            possible = []
            for hidden in (range(3) if reserve else [None]):
                available = [i < gold for i in range(3) if i != hidden]
                possible.append(sum(available) >= 2)
            rates.append(F(sum(possible), len(possible)))
        posterior = rates[0]/sum(rates)
        assert posterior == (F(3, 4) if reserve else F(1, 2))
    print('C1 informed apples likelihoods and reserve enumeration PASS')

    for first in (False, True):
        records = []
        for royal, gold in ((True, 3), (False, 2)):
            for order in permutations(range(4)):
                if order[1] < gold and (not first or order[0] >= gold):
                    records.append((F(royal), F(sum(x < gold for x in order[2:]), 2),
                                    F(2 if royal else 3, 4)))
        result = tuple(sum(row[i] for row in records)/len(records) for i in range(3))
        expected = (F(3, 7), F(5, 7), F(9, 14)) if first else (F(3, 5), F(8, 15), F(3, 5))
        assert result == expected
        print('C2 FIRST_GOLD_2' if first else 'C2 SECOND_GOLD',
              'royal / own next / other next:', *map(str, result))


def check_endpoint():
    for eta in (F(1, 20), F(1, 10), F(1, 4)):
        beta, n = F(1, 20), 1
        while (1-eta)**n > beta:
            n += 1
        for x in [F(i, 100) for i in range(101)]:
            alt = (1-2*eta)*x+eta
            assert alt >= (1-eta)*x
            assert 1-alt >= (1-eta)*(1-x)
        print('NEW endpoint test: eta=', str(eta), 'beta=1/20, total upper budget=', 2*n)
    print('  Exact rate Theta(eta^-1 log(1/beta)) follows from endpoint test and KL mixture bound')


if __name__ == '__main__':
    check_design()
    check_claims()
    check_attack()
    check_paradoxes()
    check_endpoint()
    print('PASS; proofs remain separate from finite checks; no human/model trap trials')
