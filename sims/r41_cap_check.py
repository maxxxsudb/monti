from fractions import Fraction as F


def compositions(total, parts):
    if parts == 1:
        yield (total,)
    else:
        for x in range(total + 1):
            for tail in compositions(total - x, parts - 1):
                yield (x,) + tail


def cap_bound(k, c):
    m = int(1 // c)
    remainder = 1 - m * c
    return m * max(c - F(1, k), 0) + max(remainder - F(1, k), 0)


if __name__ == '__main__':
    checked = 0
    for k in range(2, 7):
        for c in (F(1, 2), F(3, 5), F(4, 5), F(1)):
            values = []
            for counts in compositions(10, k):
                p = tuple(F(x, 10) for x in counts)
                if max(p) <= c:
                    values.append(sum(abs(x - F(1, k)) for x in p) / 2)
                    checked += 1
            assert max(values) == cap_bound(k, c)
    actual = sum(abs(x - F(1, 3)) for x in (F(3, 5), F(2, 5), F(0))) / 2
    assert actual == F(1, 3) > F(3, 5) - F(1, 3)
    print(f'PASS: {checked} capped distributions; counterexample TV=1/3 > 4/15')
