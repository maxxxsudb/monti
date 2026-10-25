"""Explicit local facts and entailed answers; no fabricated cognitive profiles."""
def query(facts, relation, subject=None, object_=None):
    assert (subject is None) != (object_ is None)
    return {o if subject is not None else s for r,s,o in facts
            if r == relation and (subject is None or s == subject)
            and (object_ is None or o == object_)}

BASE = {('produce','cow','milk'), ('drink','human','milk'), ('drink','cow','water')}
CASES = [
    ('Q1',BASE,('drink','cow',None),{'water'}),
    ('Q2',BASE,('drink',None,'milk'),{'human'}),
    ('Q3',BASE,('produce','cow',None),{'milk'}),
    ('Q4',{('produce','yak','milk'),('drink','human','milk')},('drink','yak',None),set()),
    ('Q5',{('produce','cow','milk'),('drink','cat','milk')},('drink','cow',None),set()),
    ('Q6',{('produce','cow','milk')},('drink',None,'milk'),set()),
]

def main():
    for name,facts,args,expected in CASES:
        answer = query(facts,*args)
        assert answer == expected
        print(name, sorted(answer) if answer else 'NOT_DETERMINED_BY_GIVEN_FACTS')
    assert ('produce','cow','milk') in BASE and ('drink','human','milk') in BASE
    assert ('drink','cow','milk') not in BASE
    print('PASS invalid implication has a countermodel.')
    for name,facts,args,expected in CASES[3:]:
        relation,subject,object_ = args
        fact = (relation,subject,'water') if subject is not None else (relation,'human',object_)
        assert not query(facts,*args) and query(facts|{fact},*args)
    print('PASS missing-fact completions change answers; missing does not mean false.')
    print('Former association/role arrays were hypotheses, not implemented mechanisms.')

if __name__ == '__main__':
    main()
