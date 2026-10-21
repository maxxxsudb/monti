"""Exact audit checks and generation of an unfilled 40-person pilot packet."""
from fractions import Fraction as F
from itertools import combinations
from math import comb
from pathlib import Path
import csv
import random

from focus_followup_verify_20261021 import chests


def binomial_tail(n, k, p):
    return sum(comb(n, j)*p**j*(1-p)**(n-j) for j in range(k, n+1))


def clopper_pearson(n, k):
    def invert(target, successes):
        lo, hi = 0., 1.
        for _ in range(65):
            mid = (lo+hi)/2
            if binomial_tail(n, successes, mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo+hi)/2
    return (0. if k == 0 else invert(.025, k),
            1. if k == n else invert(.975, k+1))


def main():
    count = 0
    for n in range(3, 41):
        for a in range(2, n):
            for b in range(1, a):
                pi, own, other = chests(n, a, b)
                total, d, z = a+b, a-b, a*(n-a)+b*(n-b)
                delta = F((total-n)*(total*(2*n-total)-(2*n-1)*d*d), 2*n*(n-2)*z)
                assert own-other == delta
                assert (pi < F(1, 2) and own > other) == (total > n and total*(2*n-total) > (2*n-1)*d*d)
                count += 1
    print('PASS chest identity and criterion:', count, 'exact triples')

    profiles = {'N':(1,1,1), 'L':(F(4,5),0,F(4,5)),
                'W':(0,F(4,5),F(4,5)), 'E':(0,0,0), 'LW':(0,0,F(16,25))}
    def gap(cols):
        return min(max(abs(profiles[a][i]-profiles[b][i]) for i in cols)
                   for a,b in combinations(profiles,2))
    assert gap((0,1)) == 0 and gap((0,2)) == F(4,25)
    print('PASS R1 counterexample to mandatory third probe: gamma=4/5 eps=0, IZ/IZR gap=4/25')

    sites = [(F(0), F(0), F(1,50)), (F(1), F(49,50), F(1))]
    for i in range(101):
        x = F(i,100)
        low = max(F(0), max(lower-abs(x-s) for s,lower,upper in sites))
        high = min(F(1), min(upper+abs(x-s) for s,lower,upper in sites))
        assert low == max(F(0), x-F(1,50))
        assert high == min(F(1), x+F(1,50))
    print('PASS noisy-envelope example: identity endpoints +/-1/50 certify sup-error <=1/50')

    pi, own, other = chests(5,4,3)
    restored = pi*F(4,5)+(1-pi)*F(3,5)
    assert (pi,own,other,restored) == (F(2,5),F(4,5),F(18,25),F(17,25))
    print('PASS pilot answer key: original own=.80 other=.72; returned own=.68 other=.72')
    tail = binomial_tail(20,9,F(1,4))
    assert tail <= F(1,20) < binomial_tail(20,8,F(1,4))
    print('Exact one-sided tail for 9/20 against p<=.25:', str(tail), float(tail))
    for k in (4,9,10,12):
        print('Illustrative only, NOT data:', k, '/20; 95% exact interval=', clopper_pearson(20,k))

    root = Path(__file__).resolve().parents[1]/'research/pilot-chest-40'
    labels = ['A']*20+['B']*20
    random.Random(20261021).shuffle(labels)
    with (root/'assignment.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['participant_id','version'])
        writer.writerows((f'P{i:02}',label) for i,label in enumerate(labels,1))
    responses = root/'responses.csv'
    # Never overwrite responses that may already have been entered by the user.
    if not responses.exists():
        with responses.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['participant_id','version','choice','confidence','explanation','comprehension','familiar','assistance'])
            writer.writerows([f'P{i:02}',label,'','','','','',''] for i,label in enumerate(labels,1))
    print('Pilot packet: 20 A / 20 B; no participants contacted, no answers fabricated.')


if __name__ == '__main__':
    main()
