"""Exact enumeration of physical draws, plus a finite global-bound certificate."""
from fractions import Fraction as F
import json
from pathlib import Path


def physical(n, a, b, returned):
    weight = own = other = F(0)
    for chosen, untouched in ((a, b), (b, a)):
        for first in range(n):
            if first < chosen:
                continue
            mass = F(1, 2*n)
            rest = list(range(n)) if returned else [i for i in range(n) if i != first]
            weight += mass
            own += mass*F(sum(i < chosen for i in rest), len(rest))
            other += mass*F(untouched, n)
    return own/weight, other/weight


def formula(n, a, b):
    s, d = a+b, a-b
    return F(s*(2*n-s)-(2*n-1)*d*d, 2*n*(n-1)*(2*n-s))


def main():
    best, winners, count = F(-1), [], 0
    for n in range(2, 9):
        for a in range(1, n):
            for b in range(a):
                own, other = physical(n, a, b, False)
                delta = own-other
                assert delta == formula(n, a, b)
                count += 1
                if delta > best:
                    best, winners = delta, [(n,a,b)]
                elif delta == best:
                    winners.append((n,a,b))
    assert best == F(1,9) and winners == [(3,2,1),(4,3,2)]
    assert F(2*9-3, 2*9*(9-1)) < best
    assert physical(3,2,1,False) == (F(2,3),F(5,9))
    assert physical(3,2,1,True) == (F(4,9),F(5,9))
    for pi in (F(0),F(1,5),F(1,3),F(1)):
        assert (1+pi)/2-(2-pi)/3 == (5*pi-1)/6
    assert F(2,3)-(F(2,3)+F(5,9))/2 == F(1,18)
    print('PASS action threshold pi>1/5; gain over fair random choice=1/18.')
    print('PASS physical labeled-coin enumeration:', count, 'triples; maximum=',best,'winners=',winners)
    print('Global proof additionally uses decreasing tail bound (2n-3)/(2n(n-1)), n>=9.')
    original = {'n':3,'a':2,'b':1,'observation':'silver','returned':False,
                'prior':'1/2','goal':'next_gold'}
    twin = dict(original,returned=True)
    assert [k for k in original if original[k] != twin[k]] == ['returned']
    compress = lambda task: {k:v for k,v in task.items() if k != 'returned'}
    assert compress(original) == compress(twin)
    print('PASS twin differs in exactly returned; compressed representations coincide.')
    record = {'candidate_id':'single_silver_3', 'original':original, 'control':twin,
              'normative':{'own':'2/3','other':'5/9','choice':'own'},
              'shortcut':{'erase':'returned','complete_as':True,'choice':'other'},
              'control_normative':{'own':'4/9','other':'5/9','choice':'other'},
              'status':{'normative_proven':True,'structural_lure_certified':True,
                        'behaviorally_validated':False},
              'independent_check':'enumerate labeled physical draws; account for remaining coins',
              'scope':'fixed compression/completion hypothesis, not a human error probability'}
    out = Path(__file__).resolve().parents[1]/'research/candidates/single-silver-3.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote certified candidate; no human data or model evaluation performed.')


if __name__ == '__main__':
    main()
