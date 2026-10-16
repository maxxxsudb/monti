from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, exp, log1p


def product_of(xs):
    result = Q(1)
    for x in xs:
        result *= x
    return result


def subsets(n):
    return [frozenset(xs) for r in range(n + 1) for xs in combinations(range(n), r)]


def poly_product(ps, indices):
    coefficients = [Q(1)]
    for i in indices:
        p = ps[i]
        updated = [Q(0)] * (len(coefficients) + 1)
        for j, coefficient in enumerate(coefficients):
            updated[j] += coefficient * p
            updated[j + 1] += coefficient * (1 - p)
        coefficients = updated
    return coefficients


def polynomial_mean(coefficients, moment):
    return sum((coefficient * moment(k) for k, coefficient in enumerate(coefficients)), Q(0))


def exact_batch(ps, moment):
    n = len(ps)
    mass = []
    z = Q(0)
    for bits in product((0, 1), repeat=n):
        prior = product_of(p if bit else 1 - p for p, bit in zip(ps, bits))
        weight = prior * moment(n - sum(bits))
        mass.append((bits, weight))
        z += weight
    fresh = tuple(p / (p + (1 - p) * moment(1)) for p in ps)
    values = {}
    for replaced in subsets(n):
        direct = sum((weight * product_of(bits[i] for i in range(n) if i not in replaced)
                      for bits, weight in mass), Q(0)) / z
        direct *= product_of(fresh[i] for i in replaced)
        expected = product_of(ps) / z
        expected *= polynomial_mean(poly_product(ps, replaced), moment)
        expected /= product_of(ps[i] + (1 - ps[i]) * moment(1) for i in replaced)
        assert direct == expected
        values[replaced] = direct
    return values, z, fresh


def run():
    laws = [
        lambda k: Q(1) if k == 0 else Q(1, 2),
        lambda k: (Q(1, 6) * Q(0)**k + Q(1, 3) * Q(1, 3)**k + Q(1, 2)),
        lambda k: Q(1, k + 1),
    ]
    count = 0
    interactions = 0
    for n in range(2, 6):
        families = [
            (Q(1, 2),) * n,
            tuple(Q(i + 2, i + 4) for i in range(n)),
            tuple((Q(1, 3), Q(2, 5), Q(3, 4))[i % 3] for i in range(n)),
        ]
        for ps in families:
            for moment in laws:
                values, z, fresh = exact_batch(ps, moment)
                base = values[frozenset()]
                for i, p in enumerate(ps):
                    assert values[frozenset((i,))] == base
                    others = tuple(j for j in range(n) if j != i)
                    old_quality = p * polynomial_mean(poly_product(ps, others), moment) / z
                    assert old_quality < fresh[i]
                for replaced in subsets(n):
                    for i, j in combinations((x for x in range(n) if x not in replaced), 2):
                        gap = (values[replaced | {i, j}] - values[replaced | {i}]
                               - values[replaced | {j}] + values[replaced])
                        assert gap > 0
                        interactions += 1
                if len(set(ps)) == 1:
                    p = ps[0]
                    mu = p + (1 - p) * moment(1)
                    by_count = [values[frozenset(range(r))] for r in range(n + 1)]
                    for c in (Q(0), Q(1, 100), Q(1, 5), Q(1)):
                        net = [v - c * r for r, v in enumerate(by_count)]
                        assert max(net) == max(net[0], net[-1])
                    for eps in (Q(0), Q(1, 4), Q(1, 2), Q(1)):
                        actual = sum((Q(comb(n, r)) * eps**r * (1 - eps)**(n - r) * by_count[r]
                                      for r in range(n + 1)), Q(0))
                        polynomial = [Q(1)]
                        for _ in range(n):
                            updated = [Q(0)] * (len(polynomial) + 1)
                            for k, coefficient in enumerate(polynomial):
                                updated[k] += coefficient * (1 - eps + eps * p / mu)
                                updated[k + 1] += coefficient * eps * (1 - p) / mu
                            polynomial = updated
                        assert actual == base * polynomial_mean(polynomial, moment)
                count += len(values)

    simple, _, _ = exact_batch((Q(1, 2),) * 2, laws[0])
    assert simple[frozenset()] == simple[frozenset((0,))] == Q(2, 5)
    assert simple[frozenset((0, 1))] == Q(4, 9)
    assert Q(2, 5) * (Q(1, 16) / Q(9, 16)) == Q(2, 45)

    n, p, beta = 100, 0.9, 0.01
    mu = beta + (1 - beta) * p
    pn = exp(n * log1p(p - 1))
    old = pn / (beta + (1 - beta) * pn)
    new = exp(n * log1p(-beta * (1 - p) / mu))
    assert old < 0.003 and new > 0.89
    print(f"PASS: {count} exact subset values; {interactions} strict interaction checks")
    print(f"Large example: old={old:.12f}, one replacement={old:.12f}, all={new:.12f}")


if __name__ == "__main__":
    run()
