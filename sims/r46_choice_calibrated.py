from fractions import Fraction as F


if __name__ == '__main__':
    prior = (F(1, 2), F(3, 10), F(1, 5))
    px = (F(2, 3), F(8, 9), F(1, 3))
    rows = ((F(2, 3), (F(1, 2), F(2, 5), F(1, 10))),
            (F(1, 3), (F(1, 2), F(1, 10), F(2, 5))))
    rent = F(0)
    for j, (mass, posterior) in enumerate(rows):
        channel = px if j == 0 else tuple(1-x for x in px)
        joint = tuple(p*k for p, k in zip(prior, channel))
        assert sum(joint) == mass
        assert tuple(x/mass for x in joint) == posterior
        assert posterior[0] == prior[0] == max(posterior) == F(1, 2)
        assert posterior[0] - max(posterior[1:]) == F(1, 10)
        tv = sum(abs(p-q) for p, q in zip(posterior, prior))/2
        assert tv == abs(posterior[1]-prior[1])
        rent += mass*tv
    assert rent == F(2, 15)
    print('PASS: Bayes-consistent labels; choice and confidence calibrated; side-contract edge=2/15')
