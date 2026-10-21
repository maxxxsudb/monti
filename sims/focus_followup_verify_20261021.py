"""Exact checks of the pasted follow-up; not a cognitive experiment."""
from fractions import Fraction as F
from itertools import combinations, permutations
from math import comb


def chests(n, a, b):
    wa, wb = a*(n-a), b*(n-b)
    pi = F(wa, wa+wb)
    own = (pi*(a-1)+(1-pi)*(b-1))/(n-2)
    other = (pi*b+(1-pi)*a)/n
    return pi, own, other


def main():
    count, first = 0, None
    for n in range(3, 61):
        for a in range(2, n):
            for b in range(1, a):
                pi, own, other = chests(n, a, b)
                k, d = a+b-n, a-b
                r = n*n-k*k-(2*n-1)*d*d
                numerator = n*(a*(a-1)*(n-a)+b*(b-1)*(n-b))-(n-2)*a*b*(2*n-a-b)
                assert numerator == F(k*r, 2)
                assert other-own == -F(numerator, n*(n-2)*(a*(n-a)+b*(n-b)))
                assert ((pi-F(1, 2))*(own-other) < 0) == (k != 0 and r > 0)
                if k > 0 and r > 0 and first is None:
                    first = n, a, b
                if d == 1:
                    assert r == (n-1)**2-k*k > 0
                count += 1
    assert first == (4, 3, 2)
    print('CHESTS factorization and full focus criterion:', count, 'triples PASS; first=', first)
    for triple in [(5, 4, 2), (5, 4, 3), (6, 4, 3), (6, 5, 3), (6, 5, 4)]:
        pi, own, other = chests(*triple)
        print('CORRECT TABLE', triple, 'posterior=', pi, 'own=', own,
              'other=', other, 'gap=', own-other)

    groups = {}
    for royal, gold in [(True, 3), (False, 2)]:
        for order in permutations(range(4)):
            tag = ''.join('G' if x < gold else 'S' for x in order[:2])
            groups.setdefault(tag, []).append((F(sum(x < gold for x in order[2:]), 2),
                                               F(2 if royal else 3, 4)))
    summaries = {tag: (F(len(rows), 48),
                       sum(a for a, _ in rows)/len(rows),
                       sum(b for _, b in rows)/len(rows)) for tag, rows in groups.items()}
    weighted = sum(w*max(a, b) for tag, (w, a, b) in summaries.items() if tag[1] == 'G')
    probability_g2 = sum(w for tag, (w, _, _) in summaries.items() if tag[1] == 'G')
    conditional_value = weighted/probability_g2-F(3, 5)
    full_value = sum(w*max(a, b) for w, a, b in summaries.values())-F(5, 8)
    assert conditional_value == F(1, 30)
    assert full_value == F(1, 16)
    print('VOI first colour given G2=', conditional_value, '; both colours=', full_value)

    failure = sum(F(comb(44, j))*F(1, 5)**j*F(4, 5)**(44-j) for j in range(5))
    assert failure > F(1, 80)
    print('N2 count Chernoff counterexample: actual=', float(failure), '>beta/4=0.0125')

    for i in range(1, 21):
        for j in range(i):
            g, e = F(i, 20), F(j, 20)
            profiles = [(F(1), F(1), F(1)), (g, e, g), (e, g, g),
                        (e, e, e), (g*e, g*e, g*g)]
            minimum = next(size for size in range(1, 4)
                           if any(len({tuple(p[k] for k in indices) for p in profiles}) == 5
                                  for indices in combinations(range(3), size)))
            assert minimum == (3 if g == 1 else 2)
            two = min(max(abs(a-b) for a, b in zip(p[:2], q[:2]))
                      for p, q in combinations(profiles, 2))
            three = min(max(abs(a-b) for a, b in zip(p, q))
                        for p, q in combinations(profiles, 2))
            assert two == min(g-e, e*(1-g))
            assert (three > two) == (e < g*g/(2-g))
    print('R1 original five-class model: minimum probes and strict improvement region PASS')

    for eta in (F(1, 8), F(1, 16), F(1, 32), F(1, 64)):
        eps = eta**3
        h = F(1, 2)-eps/2
        assert h-eta > F(1, 3)
        proposed_proxy_upper = 1/eta+(F(1, 4)+eta)*eps/eta**3
        print('R3 smooth rounded tent eta=', eta, 'formula proxy <=', float(proposed_proxy_upper),
              'but KL lower-bound denominator <=8eta^2=', float(8*eta*eta))
    print('PASS; symbolic proofs and uniform/nonuniform qualifications are in the review')


if __name__ == '__main__':
    main()
