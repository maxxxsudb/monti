from fractions import Fraction as F


if __name__ == '__main__':
    prior = (F(1, 2), F(3, 10), F(3, 25), F(2, 25))
    records = [
        (F(3, 5), (0, 1, 2), (F(1, 2), F(3, 10), F(1, 5), F(0))),
        (F(2, 5), (0, 1, 3), (F(1, 2), F(3, 10), F(0), F(1, 5))),
    ]
    assert tuple(sum(w*p[i] for w, _, p in records) for i in range(4)) == prior
    for lam in (F(1), F(1, 2), F(1, 10), F(1, 100)):
        rent = F(0)
        messages = [(lam*w, S, p) for w, S, p in records]
        if lam < 1:
            messages.append((1-lam, tuple(range(4)), prior))
        assert sum(w for w, _, _ in messages) == 1
        for w, S, p in messages:
            mass = sum(prior[i] for i in S)
            naive = tuple(prior[i]/mass if i in S else F(0) for i in range(4))
            assert sum(p) == 1 and max(p) == F(1, 2)
            assert all(p[i] == 0 for i in range(4) if i not in S)
            assert p[0] - max(p[1:]) >= F(1, 5)
            assert naive[0] - max(naive[1:]) >= F(1, 5)
            rent += w * sum(abs(x-y) for x, y in zip(p, naive))/2
        assert rent == lam*F(108, 1265)
    print('PASS: exact four-state witness, cap=1/2, both choice margins>=1/5, rent=lambda*108/1265')
