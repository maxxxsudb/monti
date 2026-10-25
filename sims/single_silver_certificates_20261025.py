"""Exact enumeration of physical draws, plus a finite global-bound certificate."""
from fractions import Fraction as F
import json
from pathlib import Path


def physical(n, a, b, returned, color='silver', prior=F(1,2)):
    weight = own = other = F(0)
    for chosen, untouched, type_mass in ((a, b, prior), (b, a, 1-prior)):
        for first in range(n):
            if (first < chosen) != (color == 'gold'):
                continue
            mass = type_mass/n
            rest = list(range(n)) if returned else [i for i in range(n) if i != first]
            weight += mass
            own += mass*F(sum(i < chosen for i in rest), len(rest))
            other += mass*F(untouched, n)
    return own/weight, other/weight


def solve(task):
    n,a,b = (task[k] for k in ('n','a','b'))
    assert n>=2 and 0<=b<a<n and type(task['returned']) is bool
    assert task['goal']=='next_gold' and task['observation'] in ('silver','gold')
    assert task['observation_protocol']=='one_uniform_draw_conditioned_on_color'
    prior = F(task['prior'])
    assert 0<=prior<=1
    gold = task['observation']=='gold'
    la,lb = (F(a,n),F(b,n)) if gold else (F(n-a,n),F(n-b,n))
    evidence = prior*la+(1-prior)*lb
    assert evidence>0
    pi = prior*la/evidence
    removed = int(not task['returned'])
    own = (pi*a+(1-pi)*b-int(gold)*removed)/(n-removed)
    other = (pi*b+(1-pi)*a)/n
    return {'own':str(own),'other':str(other),
            'choice':'own' if own>other else 'other' if other>own else 'equal'}


def shortcut(task, completion):
    compressed = {k:v for k,v in task.items() if k!='returned'}
    return solve(dict(compressed,returned=completion))


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
    root = Path(__file__).resolve().parents[1]
    original = json.loads((root/'research/candidates/single-silver-3.task.json').read_text(encoding='utf-8'))
    twin = dict(original,returned=True)
    assert [k for k in original if original[k] != twin[k]] == ['returned']
    compress = lambda task: {k:v for k,v in task.items() if k != 'returned'}
    assert compress(original) == compress(twin)
    print('PASS twin differs in exactly returned; compressed representations coincide.')
    normative, control, predicted = solve(original),solve(twin),shortcut(original,True)
    assert normative['choice']!=control['choice'] and predicted==control
    for color in ('silver','gold'):
        for returned in (False,True):
            task = dict(original,observation=color,returned=returned)
            exact = physical(task['n'],task['a'],task['b'],returned,color,F(task['prior']))
            assert tuple(F(solve(task)[key]) for key in ('own','other'))==exact
    cells=[]
    for color in ('silver','gold'):
        for returned in (False,True):
            task=dict(original,observation=color,returned=returned)
            cells.append({'color':color,'returned':returned,**solve(task)})
    signs=(1,-1,-1,1)
    assert [F(c['own'])-F(c['other']) for c in cells]==[F(s,9) for s in signs]
    gap4=min(s*(physical(4,3,2,r,c)[0]-physical(4,3,2,r,c)[1])
             for s,(c,r) in zip(signs,[(c,r) for c in ('silver','gold') for r in (False,True)]))
    assert gap4==F(1,20)
    print('PASS four-cell gaps +/-1/9; remaining one-cell maximizer has min gap=1/20.')
    print('PASS completion True/False executed; normative JSON calculated from TaskSpec.')
    record = {'candidate_id':'single_silver_3', 'original':original, 'control':twin,
              'normative':normative,
              'shortcut':{'erase':'returned','complete_as':True,'choice':predicted['choice']},
              'competing_shortcut':{'erase':'returned','complete_as':False,'choice':shortcut(original,False)['choice']},
              'control_normative':control, 'four_cells':cells,
              'status':{'normative_proven':True,'representation_collision_proven':True,
                        'shortcut_executable':True,'shortcut_prevalence_estimated':False,
                        'self_check_failure_tested':False,'behaviorally_validated':False},
              'independent_check':'enumerate labeled physical draws; account for remaining coins',
              'scope':'fixed compression/completion hypothesis, not a human error probability'}
    out = Path(__file__).resolve().parents[1]/'research/candidates/single-silver-3.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote certified candidate; no human data or model evaluation performed.')


if __name__ == '__main__':
    main()
